#!/usr/bin/env python3
"""Edge-TTS wrapper for Educational Material Maker.

Usage:
    py scripts/synthesize_tts.py <input.txt> <output.mp3> [--voice <voice>]

Dependencies:
    pip install edge-tts
"""

import argparse
import asyncio
import sys
from pathlib import Path


async def synthesize(text: str, output: str, voice: str) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output)


def main() -> None:
    parser = argparse.ArgumentParser(description="Edge-TTS synthesis")
    parser.add_argument("input", help="Input text file path")
    parser.add_argument("output", help="Output mp3 file path")
    parser.add_argument(
        "--voice",
        default="zh-TW-HsiaoChenNeural",
        help="Edge-TTS voice ID (default: zh-TW-HsiaoChenNeural)",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    text = input_path.read_text(encoding="utf-8").strip()
    if not text:
        print(f"Warning: empty text in {args.input}, skipping", file=sys.stderr)
        sys.exit(0)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        asyncio.run(synthesize(text, str(output_path), args.voice))
    except Exception as e:
        print(f"Error: TTS failed: {e}", file=sys.stderr)
        sys.exit(1)

    if not output_path.exists():
        print(f"Error: output file not created: {args.output}", file=sys.stderr)
        sys.exit(1)

    print(f"Done: {args.output}")


if __name__ == "__main__":
    main()
