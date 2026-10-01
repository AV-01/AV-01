#!/usr/bin/env python3
"""Render a transparent PNG heading from a TrueType/OpenType font.

Examples:
  python render_heading.py "ABOUT ME" assets/about-black.png --color black
  python render_heading.py "ABOUT ME" assets/about-white.png --color white
  python render_heading.py "MY PROJECT" assets/project.png --size 96 --color white --outline-color black --outline-width 3
"""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


SCRIPT_DIRECTORY = Path(__file__).resolve().parent
DEFAULT_FONT = SCRIPT_DIRECTORY / "deltarune.ttf"


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create a transparent PNG heading using a font file."
    )
    parser.add_argument("text", help="Heading text. Use \\n for multiple lines.")
    parser.add_argument("output", type=Path, help="Output PNG path.")
    parser.add_argument(
        "--font",
        type=Path,
        default=DEFAULT_FONT,
        help=f"Font file to use (default: {DEFAULT_FONT.name}).",
    )
    parser.add_argument("--size", type=int, default=96, help="Font size in pixels.")
    parser.add_argument("--color", default="black", help="Text color (default: black).")
    parser.add_argument(
        "--outline-color", default=None, help="Optional outline color, such as black."
    )
    parser.add_argument(
        "--outline-width", type=int, default=0, help="Outline width in pixels."
    )
    parser.add_argument("--padding", type=int, default=12, help="Transparent padding in pixels.")
    parser.add_argument(
        "--line-spacing", type=int, default=4, help="Extra pixels between lines."
    )
    return parser.parse_args()


def main() -> None:
    args = arguments()
    if args.size <= 0 or args.padding < 0 or args.outline_width < 0:
        raise SystemExit("--size must be positive; --padding and --outline-width cannot be negative.")
    if not args.font.is_file():
        raise SystemExit(f"Font file not found: {args.font}")

    font = ImageFont.truetype(args.font, args.size)
    text = args.text.replace("\\n", "\n")
    stroke_width = args.outline_width
    stroke_fill = args.outline_color or args.color

    # Measure on a temporary canvas, then make a precisely sized PNG.
    measure = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    left, top, right, bottom = measure.multiline_textbbox(
        (0, 0), text, font=font, spacing=args.line_spacing, stroke_width=stroke_width
    )
    width = right - left + args.padding * 2
    height = bottom - top + args.padding * 2
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.multiline_text(
        (args.padding - left, args.padding - top),
        text,
        font=font,
        fill=args.color,
        spacing=args.line_spacing,
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    image.save(args.output, "PNG")
    print(f"Wrote {args.output} ({width}x{height}px, transparent background)")


if __name__ == "__main__":
    main()
