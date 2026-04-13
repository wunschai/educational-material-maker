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


async def synthesize(text: str, output: str, voice: str, srt_output: str | None = None) -> None:
    import edge_tts

    communicate = edge_tts.Communicate(text, voice)

    if srt_output:
        # Stream mode: capture audio + word boundary timing for subtitles
        submaker = edge_tts.SubMaker()
        with open(output, "wb") as audio_file:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_file.write(chunk["data"])
                else:
                    submaker.feed(chunk)
        # Write SRT with real speech timing from Edge-TTS word boundaries
        srt_content = submaker.get_srt()
        Path(srt_output).parent.mkdir(parents=True, exist_ok=True)
        Path(srt_output).write_text(srt_content, encoding="utf-8")
    else:
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
    parser.add_argument(
        "--srt",
        default=None,
        help="Output SRT subtitle file (uses Edge-TTS word boundary timing for exact sync)",
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
        asyncio.run(synthesize(text, str(output_path), args.voice, srt_output=args.srt))
    except Exception as e:
        print(f"Error: TTS failed: {e}", file=sys.stderr)
        sys.exit(1)

    if not output_path.exists():
        print(f"Error: output file not created: {args.output}", file=sys.stderr)
        sys.exit(1)

    print(f"Done: {args.output}")


if __name__ == "__main__":
    main()
