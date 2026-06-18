# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/kbits.c

Reads JIS/Kuten bitmap glyphs from a textual bits file.

Key function:
- `kreadbits(file, n, chars, size, bits, doneptr)` opens the bits file, skips two header lines, parses each glyph record, converts hex bitmap rows to bytes, stores matching glyphs, compacts present glyphs, and returns a Plan 9 `Bitmap`.

Notable behavior:
- Uses `strtol(p+17, ...)` for the glyph code and `p += 25` for bitmap data, so it depends on a fixed input record layout.
- Missing glyph diagnostics are present but commented out.
