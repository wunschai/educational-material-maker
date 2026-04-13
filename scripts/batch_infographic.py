#!/usr/bin/env python3
"""Batch NotebookLM infographic generation for all slides.

Usage:
    py scripts/batch_infographic.py <slug> [--style professional] [--pages all|1,3,5-8]
"""

import argparse
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path

# Force UTF-8 for all I/O on Windows
os.environ["PYTHONIOENCODING"] = "utf-8"
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# Rate limit handling
MAX_RETRIES = 3
INITIAL_BACKOFF = 60  # seconds


class RateLimitError(Exception):
    pass


def run_nlm(args: list[str], timeout: int = 30) -> str:
    env = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONLEGACYWINDOWSSTDIO": "utf-8"}
    result = subprocess.run(
        ["nlm"] + args,
        capture_output=True, timeout=timeout,
        env=env,
    )
    stdout = result.stdout.decode("utf-8", errors="replace") if result.stdout else ""
    stderr = result.stderr.decode("utf-8", errors="replace") if result.stderr else ""
    combined = stdout + stderr

    # Detect rate limit / quota errors
    if any(sig in combined for sig in ["code 8", "Could not create infographic", "429", "RESOURCE_EXHAUSTED"]):
        raise RateLimitError(combined[:300])

    return combined


def parse_slides(slides_path: Path) -> list[dict]:
    """Split slides.md into per-page content."""
    text = slides_path.read_text(encoding="utf-8")
    # Remove YAML frontmatter
    text = re.sub(r"^---\n.*?\n---\n", "", text, count=1, flags=re.DOTALL)
    # Split by ---
    raw_pages = re.split(r"\n---\n", text)
    pages = []
    for i, content in enumerate(raw_pages):
        content = content.strip()
        if not content:
            continue
        # Extract title from first heading
        title_match = re.search(r"^#+\s+(.+)$", content, re.MULTILINE)
        title = title_match.group(1) if title_match else f"Slide {i+1}"
        # Remove speaker notes for the outline (keep them separate)
        clean = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL).strip()
        pages.append({"num": i + 1, "title": title, "content": content, "clean": clean})
    return pages


def extract_reference(research_path: Path, slide_content: str) -> str:
    """Extract relevant research paragraphs for a slide."""
    research = research_path.read_text(encoding="utf-8")
    # Get all concept sections
    sections = re.split(r"\n### \d+\. ", research)
    if len(sections) <= 1:
        return research[:2000]  # fallback: first 2000 chars

    # Score each section by keyword overlap with slide content
    slide_words = set(re.findall(r"[\u4e00-\u9fff]{2,}", slide_content))
    scored = []
    for sec in sections[1:]:
        sec_words = set(re.findall(r"[\u4e00-\u9fff]{2,}", sec))
        overlap = len(slide_words & sec_words)
        scored.append((overlap, sec))

    # Take top 2 most relevant sections
    scored.sort(reverse=True)
    top = scored[:2]
    result = "\n\n".join(s for _, s in top)
    return result[:2000]


def generate_infographic(
    slide: dict, research_ref: str, topic: str,
    style: str, out_path: Path,
) -> bool:
    """Generate one infographic via NotebookLM."""
    num = slide["num"]
    title = slide["title"]
    print(f"\n{'='*60}")
    print(f"Slide {num}: {title}")
    print(f"{'='*60}")

    # 1. Create notebook
    print("  [1/6] Creating notebook...")
    output = run_nlm(["notebook", "create", f"edu-slide-{num:02d}"])
    id_match = re.search(r"ID:\s*(\S+)", output)
    if not id_match:
        print(f"  ERROR: failed to create notebook: {output[:200]}")
        return False
    nb_id = id_match.group(1)

    # 2. Add outline source
    print("  [2/6] Adding outline source...")
    outline_tmp = Path(tempfile.gettempdir()) / f"edu-slide-{num:02d}-outline.md"
    outline_content = f"# {topic} — 第 {num} 頁：{title}\n\n{slide['clean']}"
    outline_tmp.write_text(outline_content, encoding="utf-8")
    run_nlm(["source", "add", nb_id, "--text", str(outline_tmp)])

    # 3. Add reference source
    print("  [3/6] Adding reference source...")
    ref_tmp = Path(tempfile.gettempdir()) / f"edu-slide-{num:02d}-ref.md"
    ref_content = f"# 參考資料：{topic}\n\n{research_ref}"
    ref_tmp.write_text(ref_content, encoding="utf-8")
    run_nlm(["source", "add", nb_id, "--text", str(ref_tmp)])

    # 4. Generate infographic (with retry + exponential backoff)
    print(f"  [4/6] Generating infographic (style={style})...")
    focus = f"這是「{topic}」教學簡報的第 {num} 頁，主題是「{title}」。請以大綱檔為核心結構生成教學用資訊圖表。語言使用繁體中文。"
    created = False
    for attempt in range(MAX_RETRIES):
        try:
            run_nlm([
                "infographic", "create", nb_id,
                "--style", style,
                "--orientation", "landscape",
                "--detail", "standard",
                "--language", "zh-TW",
                "--focus", focus,
                "--confirm",
            ], timeout=60)
            created = True
            break
        except RateLimitError as e:
            wait = INITIAL_BACKOFF * (2 ** attempt)
            print(f"  RATE LIMITED (attempt {attempt+1}/{MAX_RETRIES}), waiting {wait}s...")
            time.sleep(wait)

    if not created:
        print(f"  ERROR: rate limit not resolved after {MAX_RETRIES} retries")
        run_nlm(["notebook", "delete", nb_id, "--confirm"])
        outline_tmp.unlink(missing_ok=True)
        ref_tmp.unlink(missing_ok=True)
        raise RateLimitError("daily limit likely reached")

    # 5. Poll until done (max 5 min)
    print("  [5/6] Waiting for completion", end="", flush=True)
    done = False
    for _ in range(20):
        time.sleep(15)
        print(".", end="", flush=True)
        try:
            status = run_nlm(["studio", "status", nb_id])
        except RateLimitError:
            continue  # polling shouldn't be rate-limited, but handle gracefully
        if '"completed"' in status:
            done = True
            break
    print()

    if not done:
        print(f"  TIMEOUT: slide {num} did not complete in 5 min")
        run_nlm(["notebook", "delete", nb_id, "--confirm"])
        return False

    # 6. Download + cleanup
    print(f"  [6/6] Downloading → {out_path.name}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    run_nlm(["download", "infographic", nb_id, "-o", str(out_path)], timeout=60)
    run_nlm(["notebook", "delete", nb_id, "--confirm"])

    # Cleanup temp files
    outline_tmp.unlink(missing_ok=True)
    ref_tmp.unlink(missing_ok=True)

    if out_path.exists():
        size_mb = out_path.stat().st_size / 1024 / 1024
        print(f"  ✓ Done ({size_mb:.1f} MB)")
        return True
    else:
        print(f"  ERROR: output file not created")
        return False


def parse_pages_arg(pages_str: str, total: int) -> list[int]:
    """Parse '1,3,5-8' into [1,3,5,6,7,8]."""
    if pages_str == "all":
        return list(range(1, total + 1))
    result = []
    for part in pages_str.split(","):
        if "-" in part:
            start, end = map(int, part.split("-"))
            result.extend(range(start, end + 1))
        else:
            result.append(int(part))
    return sorted(set(r for r in result if 1 <= r <= total))


def main():
    parser = argparse.ArgumentParser(description="Batch NotebookLM infographic generation")
    parser.add_argument("slug", help="Lesson slug")
    parser.add_argument("--style", default="professional", help="NotebookLM style")
    parser.add_argument("--pages", default="all", help="Pages to process: all or 1,3,5-8")
    parser.add_argument("--lesson-dir", default="lessons", help="Lessons base directory")
    args = parser.parse_args()

    lesson_path = Path(args.lesson_dir) / args.slug
    slides_path = lesson_path / "slides.md"
    research_path = lesson_path / "topic.research.md"
    infographics_dir = lesson_path / "infographics"

    if not slides_path.exists():
        print(f"Error: {slides_path} not found", file=sys.stderr)
        sys.exit(1)
    if not research_path.exists():
        print(f"Error: {research_path} not found", file=sys.stderr)
        sys.exit(1)

    # Check nlm is available
    try:
        run_nlm(["--version"], timeout=10)
    except FileNotFoundError:
        print("Error: nlm CLI not found. Run: pip install notebooklm-mcp-cli", file=sys.stderr)
        sys.exit(1)

    # Parse slides
    pages = parse_slides(slides_path)
    total = len(pages)
    print(f"Parsed {total} slides from {slides_path}")

    # Determine which pages to process
    target_pages = parse_pages_arg(args.pages, total)
    print(f"Will process {len(target_pages)} pages: {target_pages}")
    print(f"Style: {args.style}")
    print(f"Estimated time: {len(target_pages) * 1.5:.0f}-{len(target_pages) * 2:.0f} minutes")
    print()

    # Extract topic from first heading
    topic = "教學主題"
    for p in pages:
        if p["title"] and not p["title"].startswith("Slide"):
            topic = re.sub(r"[#*_]", "", p["title"]).strip()
            break

    # Skip pages that already have infographics
    existing = {int(p.stem.split("-")[1]) for p in infographics_dir.glob("slide-*.png")} if infographics_dir.exists() else set()
    remaining = [p for p in target_pages if p not in existing]
    if existing:
        print(f"Skipping {len(existing)} already-generated pages: {sorted(existing)}")
    if not remaining:
        print("All target pages already have infographics. Nothing to do.")
        return
    print(f"Remaining: {len(remaining)} pages: {remaining}")

    # Process pages in parallel batches
    from concurrent.futures import ThreadPoolExecutor, as_completed

    BATCH_SIZE = int(os.environ.get("NLM_PARALLEL", "1"))
    print(f"Parallel workers: {BATCH_SIZE}")
    print(f"Estimated time: {len(remaining) * 1.5 / BATCH_SIZE:.0f}-{len(remaining) * 2 / BATCH_SIZE:.0f} minutes")

    page_map = {p["num"]: p for p in pages}
    success = 0
    failed = []
    start_time = time.time()
    consecutive_rate_limits = 0

    # Serial processing (NotebookLM doesn't support concurrent requests)
    for num in remaining:
        page = page_map[num]
        ref = extract_reference(research_path, page["content"])
        out = infographics_dir / f"slide-{num:02d}.png"

        try:
            ok = generate_infographic(page, ref, topic, args.style, out)
        except RateLimitError:
            consecutive_rate_limits += 1
            failed.append(num)
            if consecutive_rate_limits >= 2:
                not_done = remaining[remaining.index(num):]
                print(f"\n  DAILY LIMIT REACHED after {success} pages.")
                print(f"  Completed: {sorted(set(remaining[:remaining.index(num)]) - set(failed))}")
                print(f"  Remaining: {not_done}")
                print(f"  Re-run with: --pages {','.join(str(p) for p in not_done)}")
                break
            continue
        else:
            consecutive_rate_limits = 0

        if ok:
            success += 1
        else:
            failed.append(num)

    elapsed = time.time() - start_time
    print(f"\n{'='*60}")
    print(f"DONE: {success}/{len(remaining)} new pages in {elapsed/60:.1f} minutes")
    print(f"Total infographics: {success + len(existing)}/{len(target_pages)}")
    if failed:
        print(f"FAILED pages: {failed}")
    print(f"Output: {infographics_dir}/")


if __name__ == "__main__":
    main()
