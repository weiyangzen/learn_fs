# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/bbits.c

Reads Big5 bitmap glyphs from a raw font bitfile.

Key function:
- `breadbits(file, n, chars, size, bits, doneptr)` opens a Big5 bits file, seeks to each requested Big5 ordinal, copies glyph rows into an interleaved bitmap buffer, compacts found glyphs, allocates a Plan 9 `Bitmap`, and writes bitmap data into it.

Important details:
- `Charsperfont = 157`, matching `BIG5FONT`.
- Contains Big5 void-range constants and a hard-coded 16x16 `missing` glyph pattern to detect absent glyphs.
- Handles Big5 file layout holes with offset adjustments before seek.
- `done[i]` marks glyphs included in the compacted bitmap.

Dependencies:
- Plan 9 graphics `Bitmap`, `balloc`, `wrbitmap`.
