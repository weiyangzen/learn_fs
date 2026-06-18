# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zpaint.c

## Purpose
Implements basic painting operators and small nonstandard painting helpers.

## Key Functions
- `zfill()`, `zeofill()`, and `zstroke()` wrap standard path painting.
- `zfillpage()` fills the entire page.
- `zimagepath()` converts bitmap data into a path.

## Important Behavior
- `.imagepath` validates integer width/height and readable string data.
- Bitmap data length must cover `ceil(width / 8) * height`.
- Painting itself is delegated to Ghostscript graphics APIs.

## Research Notes
Thin painting operator layer over `gspaint.h`.
