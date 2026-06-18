# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/font/qbits.c

Reads GB quwei-encoded bitmap glyphs from a textual bits file.

Key function:
- `qreadbits(file, n, chars, size, bits, doneptr)` scans each line, parses the first four decimal digits as quwei code, converts following hex bitmap rows to bytes, stores matching glyphs, compacts found glyphs, and returns a Plan 9 `Bitmap`.

Notable behavior:
- Similar to `kreadbits`, but code parsing uses four leading decimal digits and bitmap data begins at `p += 5`.
- Missing glyph diagnostics are commented out.
- The file argument is still opened even though `main.c` lists no default 16-bit file for `Gb_qw`; callers must pass `-f`.
