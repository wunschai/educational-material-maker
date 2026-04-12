#!/usr/bin/env python3
"""Playwright screenshot + ffmpeg compose for Educational Material Maker.

Usage:
    py scripts/render_video.py <slides.html> <audio_dir> <output.mp4> [--resolution 1280x720]

Flow:
    1. Playwright opens slides.html, screenshots each slide as PNG
    2. ffprobe gets each audio file's duration
    3. ffmpeg composites PNG + mp3 → segment mp4 (per slide)
    4. ffmpeg concat all segments → final mp4
    5. Cleanup frames/ and segments/

Dependencies:
    pip install playwright && playwright install chromium
    ffmpeg in PATH
"""

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def check_dependencies() -> None:
    if not shutil.which("ffmpeg"):
        print("Error: ffmpeg not found in PATH. Please install ffmpeg.", file=sys.stderr)
        sys.exit(1)
    if not shutil.which("ffprobe"):
        print("Error: ffprobe not found in PATH. Please install ffmpeg.", file=sys.stderr)
        sys.exit(1)
    try:
        from playwright.sync_api import sync_playwright  # noqa: F401
    except ImportError:
        print(
            "Error: playwright not installed. Run: pip install playwright && playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)


def screenshot_slides(html_path: str, frames_dir: Path, width: int, height: int) -> int:
    from playwright.sync_api import sync_playwright

    frames_dir.mkdir(parents=True, exist_ok=True)
    file_url = Path(html_path).resolve().as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": width, "height": height})
        page.goto(file_url, wait_until="networkidle")

        slide_count = page.evaluate("document.querySelectorAll('section').length")
        if slide_count == 0:
            print("Error: no slides found in HTML", file=sys.stderr)
            browser.close()
            sys.exit(1)

        # Marp HTML uses presentation mode — slides are NOT vertically stacked.
        # Navigate using keyboard ArrowRight (most reliable across Marp versions).
        # First slide is already visible after page load.
        for i in range(slide_count):
            if i > 0:
                page.keyboard.press("ArrowRight")
            page.wait_for_timeout(500)
            out = frames_dir / f"slide-{i + 1:02d}.png"
            page.screenshot(path=str(out))
            print(f"  Screenshot: {out.name}")

        browser.close()

    return slide_count


def get_audio_duration(mp3_path: str) -> float:
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            mp3_path,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return 3.0  # fallback: 3 seconds for missing/broken audio
    info = json.loads(result.stdout)
    return float(info.get("format", {}).get("duration", 3.0))


def compose_segments(
    frames_dir: Path,
    audio_dir: Path,
    segments_dir: Path,
    slide_count: int,
    buffer: float,
) -> list[Path]:
    segments_dir.mkdir(parents=True, exist_ok=True)
    segment_paths = []

    for i in range(1, slide_count + 1):
        frame = frames_dir / f"slide-{i:02d}.png"
        audio = audio_dir / f"slide-{i:02d}.mp3"
        seg_out = segments_dir / f"seg-{i:02d}.mp4"

        if not frame.exists():
            print(f"  Warning: missing frame {frame.name}, skipping", file=sys.stderr)
            continue

        if audio.exists():
            duration = get_audio_duration(str(audio)) + buffer
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", str(frame),
                "-i", str(audio),
                "-c:v", "libx264", "-tune", "stillimage",
                "-c:a", "aac", "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-t", f"{duration:.2f}",
                "-shortest",
                str(seg_out),
            ]
        else:
            # No audio for this slide: 3 seconds of silence
            duration = 3.0
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", str(frame),
                "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                "-c:v", "libx264", "-tune", "stillimage",
                "-c:a", "aac", "-b:a", "192k",
                "-pix_fmt", "yuv420p",
                "-t", f"{duration:.2f}",
                str(seg_out),
            ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"  Warning: ffmpeg failed for slide {i}: {result.stderr[:200]}", file=sys.stderr)
            continue

        segment_paths.append(seg_out)
        print(f"  Segment: {seg_out.name} ({duration:.1f}s)")

    return segment_paths


def concat_segments(segment_paths: list[Path], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    filelist = output.parent / "filelist.txt"

    with open(filelist, "w", encoding="utf-8") as f:
        for seg in segment_paths:
            f.write(f"file '{seg.resolve()}'\n")

    result = subprocess.run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(filelist),
            "-c", "copy",
            str(output),
        ],
        capture_output=True,
        text=True,
    )

    filelist.unlink(missing_ok=True)

    if result.returncode != 0:
        print(f"Error: concat failed: {result.stderr[:300]}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render slides + audio to mp4")
    parser.add_argument("html", help="slides.html path")
    parser.add_argument("audio_dir", help="audio/ directory with slide-NN.mp3 files")
    parser.add_argument("output", help="output mp4 path")
    parser.add_argument("--resolution", default="1280x720", help="WxH (default: 1280x720)")
    args = parser.parse_args()

    check_dependencies()

    width, height = map(int, args.resolution.split("x"))
    html_path = Path(args.html)
    audio_dir = Path(args.audio_dir)
    output_path = Path(args.output)

    if not html_path.exists():
        print(f"Error: HTML not found: {args.html}", file=sys.stderr)
        sys.exit(1)
    if not audio_dir.exists():
        print(f"Error: audio dir not found: {args.audio_dir}", file=sys.stderr)
        sys.exit(1)

    lesson_dir = html_path.parent
    frames_dir = lesson_dir / "frames"
    segments_dir = lesson_dir / "segments"

    print(f"[1/4] Screenshotting slides ({width}x{height})...")
    slide_count = screenshot_slides(str(html_path), frames_dir, width, height)
    print(f"  {slide_count} slides captured")

    print("[2/4] Composing segments (PNG + MP3 → MP4)...")
    segment_paths = compose_segments(frames_dir, audio_dir, segments_dir, slide_count, buffer=1.5)
    if not segment_paths:
        print("Error: no segments produced", file=sys.stderr)
        sys.exit(1)
    print(f"  {len(segment_paths)} segments")

    print("[3/4] Concatenating segments...")
    concat_segments(segment_paths, output_path)

    print("[4/4] Cleaning up frames/ and segments/...")
    shutil.rmtree(frames_dir, ignore_errors=True)
    shutil.rmtree(segments_dir, ignore_errors=True)

    if output_path.exists():
        size_mb = output_path.stat().st_size / 1024 / 1024
        print(f"Done: {output_path} ({size_mb:.1f} MB)")
    else:
        print("Error: output mp4 not created", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
