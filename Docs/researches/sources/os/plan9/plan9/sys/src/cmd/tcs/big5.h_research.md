# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/big5.h

Header for Big5 conversion tables.

Defines:
- `BIG5MAX 13973`: number of Big5 ordinal slots.
- `BIG5FONT 157`: number of trailing-byte positions per lead-byte row.

Declares:
- `extern long tabbig5[BIG5MAX]`.

Used by:
- `big5.c`, `conv_big5.c`, and `tcs/font/bmap.c`.
