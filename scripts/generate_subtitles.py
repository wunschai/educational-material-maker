#!/usr/bin/env python3
"""Generate SRT subtitles from narration text + audio timing.

Usage:
    py scripts/generate_subtitles.py <narration_dir> <audio_dir> <output.srt>

Reads narration/slide-NN.txt for text, audio/slide-NN.mp3 for timing.
Each slide becomes one SRT entry spanning the audio duration.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path


def get_audio_duration(mp3_path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(mp3_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        return 3.0
    info = json.loads(result.stdout)
    return float(info.get("format", {}).get("duration", 3.0))


def format_srt_time(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    parser = argparse.ArgumentParser(description="Generate SRT subtitles")
    parser.add_argument("narration_dir", help="Directory with slide-NN.txt files")
    parser.add_argument("audio_dir", help="Directory with slide-NN.mp3 files (for timing)")
    parser.add_argument("output", help="Output SRT file path")
    parser.add_argument("--text-suffix", default="", help="Read slide-NN<suffix>.txt (e.g., '.original', '.subtitle')")
    args = parser.parse_args()

    narration_dir = Path(args.narration_dir)
    audio_dir = Path(args.audio_dir)
    text_suffix = args.text_suffix
    output_path = Path(args.output)

    if not narration_dir.exists():
        print(f"Error: narration dir not found: {narration_dir}", file=sys.stderr)
        sys.exit(1)
    if not audio_dir.exists():
        print(f"Error: audio dir not found: {audio_dir}", file=sys.stderr)
        sys.exit(1)

    # Collect slides — use suffix if specified (e.g., slide-01.original.txt)
    pattern = f"slide-*{text_suffix}.txt"
    txt_files = sorted(narration_dir.glob(pattern))
    if not txt_files:
        print("Error: no slide-*.txt files found", file=sys.stderr)
        sys.exit(1)

    entries = []
    current_time = 0.0

    for txt_file in txt_files:
        # Extract slide number regardless of suffix (slide-01.original → slide-01)
        slide_num = txt_file.stem.split(".")[0]  # e.g., "slide-01"
        text = txt_file.read_text(encoding="utf-8").strip()
        if not text:
            # Silent slide — still advance timing
            mp3 = audio_dir / f"{slide_num}.mp3"
            duration = get_audio_duration(mp3) if mp3.exists() else 3.0
            current_time += duration + 1.5
            continue

        mp3 = audio_dir / f"{slide_num}.mp3"
        duration = get_audio_duration(mp3) if mp3.exists() else 3.0

        start = current_time
        end = current_time + duration

        entries.append({
            "index": len(entries) + 1,
            "start": format_srt_time(start),
            "end": format_srt_time(end),
            "text": text,
        })

        current_time = end + 1.5  # buffer between slides

    # Write SRT
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        for entry in entries:
            f.write(f"{entry['index']}\n")
            f.write(f"{entry['start']} --> {entry['end']}\n")
            f.write(f"{entry['text']}\n\n")

    print(f"Done: {output_path} ({len(entries)} entries, {format_srt_time(current_time)} total)")


if __name__ == "__main__":
    main()
