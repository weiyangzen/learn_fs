# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postdmd/postdmd.c

`postdmd.c` translates DMD bitmap files into PostScript bitmap pages.

Main flow:
- Standard translator sequence: signal setup, DSC header/prologue, options, setup, arguments, trailer/accounting.
- `bitmap()` reads one or more bitmaps from each input file and emits one PostScript page per bitmap.
- `dimensions()` detects bitmap format and dimensions.
- `addrast()` decodes input compressed raster patterns into a scanline buffer.
- `putrast()` re-encodes scanlines into a PostScript-friendly pattern/repeat format.
- `redirect()` implements page filtering.

Input formats:
- Supports Eighth/Ninth Edition bitfile format, detected by an initial zero 16-bit value followed by origin/corner coordinates.
- Also supports a simpler format where first two 16-bit values are scanlines and patterns.
- Eighth Edition raster lines are XORed with the previous line on host by default unless `-u` disables undoing and leaves it for the printer/prologue.

Options:
- `-b` controls bytes per output pattern; non-positive disables pattern chunking.
- `-f` flips/ones-complements output.
- Standard options include copies, magnification, forms per page, page list, orientation, offsets, accounting, copy-through, encoding, prologue, pass-through, requests, debug, ignore-fatal.

Output:
- Emits `v8format flip scanlength scanlines bitmap` call.
- Tracks maximum bounding box in `bbox`.
- Each scanline is emitted as repeated hex pattern runs terminated by `0`.

Limitations and risks:
- Uses K&R C and unprototyped libc calls.
- Raster allocation is based on dimensions from input; malformed dimensions can drive memory use.
- `putrast()` pattern scanning relies on `eptr` bounds checks through `patncmp()`.
- If input compressed pattern counts do not match expected totals, it raises fatal “bitmap format error”.

Filesystem relevance: none direct; it is a bitmap-to-PostScript user utility.
