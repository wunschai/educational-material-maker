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
    scale_to: str | None = None,
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

        # Build video filter for scaling if using infographics (variable resolution)
        vf = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" if scale_to else None

        if audio.exists():
            duration = get_audio_duration(str(audio)) + buffer
            cmd = [
                "ffmpeg", "-y",
                "-loop", "1", "-i", str(frame),
                "-i", str(audio),
                "-c:v", "libx264", "-tune", "stillimage",
                "-c:a", "aac", "-b:a", "192k",
                "-pix_fmt", "yuv420p",
            ]
            if vf:
                cmd.extend(["-vf", vf])
            cmd.extend(["-t", f"{duration:.2f}", "-shortest", str(seg_out)])
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
            ]
            if vf:
                cmd.extend(["-vf", vf])
            cmd.extend(["-t", f"{duration:.2f}", str(seg_out)])

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
    parser.add_argument("--subtitles", default=None, help="SRT subtitle file to burn in")
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
    infographics_dir = lesson_dir / "infographics"
    frames_dir = lesson_dir / "frames"
    segments_dir = lesson_dir / "segments"

    # Hybrid mode: use infographics where available, Playwright screenshots for the rest
    has_infographics = infographics_dir.exists() and any(infographics_dir.glob("slide-*.png"))

    print(f"[1/4] Capturing slide frames ({width}x{height})...")
    # Always screenshot ALL slides via Playwright first
    slide_count = screenshot_slides(str(html_path), frames_dir, width, height)
    print(f"  {slide_count} slides screenshotted")

    # Then overlay infographics where they exist
    use_infographics = False
    if has_infographics:
        infographic_files = sorted(infographics_dir.glob("slide-*.png"))
        replaced = 0
        for inf in infographic_files:
            target = frames_dir / inf.name
            if target.exists():
                target.unlink()
            import shutil as _sh
            _sh.copy2(inf, target)
            replaced += 1
        print(f"  {replaced} pages replaced with infographics (hybrid mode)")
        use_infographics = replaced > 0

    print("[2/4] Composing segments (PNG + MP3 → MP4)...")
    segment_paths = compose_segments(
        frames_dir, audio_dir, segments_dir, slide_count, buffer=1.5,
        scale_to=f"{width}:{height}" if use_infographics else None,
    )
    if not segment_paths:
        print("Error: no segments produced", file=sys.stderr)
        sys.exit(1)
    print(f"  {len(segment_paths)} segments")

    print("[3/4] Concatenating segments...")
    concat_segments(segment_paths, output_path)

    # [3.5] Burn subtitles if provided
    if args.subtitles and Path(args.subtitles).exists():
        print(f"[3.5] Burning subtitles: {args.subtitles}")
        subtitled_output = output_path.with_stem(output_path.stem + "-sub")
        # Copy SRT next to the output mp4 to avoid Windows path escaping issues
        # ffmpeg subtitles filter struggles with colons/backslashes in absolute paths
        local_srt = output_path.parent / "temp_subs.srt"
        shutil.copy2(Path(args.subtitles), local_srt)
        # Run ffmpeg from the output directory so relative path works
        sub_cmd = [
            "ffmpeg", "-y",
            "-i", output_path.name,
            "-vf", "subtitles=temp_subs.srt:force_style='FontSize=20,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,MarginV=30'",
            "-c:a", "copy",
            subtitled_output.name,
        ]
        result = subprocess.run(sub_cmd, capture_output=True, text=True, cwd=str(output_path.parent))
        local_srt.unlink(missing_ok=True)
        if result.returncode == 0 and subtitled_output.exists():
            output_path.unlink()
            subtitled_output.rename(output_path)
            print(f"  Subtitles burned in successfully")
        else:
            print(f"  Warning: subtitle burn failed, keeping video without subs", file=sys.stderr)
            if result.stderr:
                print(f"  {result.stderr[:200]}", file=sys.stderr)
            subtitled_output.unlink(missing_ok=True)

    print("[4/4] Cleaning up intermediate files...")
    # Always delete frames/ (screenshots + copied infographics = intermediate)
    # Never delete infographics/ (user-generated content)
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
