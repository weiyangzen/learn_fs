# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/gbits.c

Reads GB glyphs from a BDF font file.

Key function:
- `greadbits(file, n, chars, size, bits, doneptr)` scans BDF `STARTCHAR` records, reads `ENCODING` and `BITMAP`, converts hex rows to bytes, copies matching glyphs into an interleaved bitmap, compacts found glyphs, and returns a Plan 9 `Bitmap`.

Helper:
- `field(bf, name)` advances to a required BDF field or exits on malformed input.

Encoding:
- BDF `ENCODING` is converted to GB ordinal using `(high - 0xA0)*100 + (low - 0xA0)`.

Notable behavior:
- Fixed `buf[1024]` is assumed big enough for one glyph bitmap.
- Uses lowercase hex digit table only.
