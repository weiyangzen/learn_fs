# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postdmd/postdmd.c

PostScript translator for DMD bitmap files, including Eighth/Ninth Edition bitfile format handling.

Key responsibilities:
- Emits PostScript job structure and copies the `POSTDMD` prologue.
- Reads one or more bitmaps per input file and prints each bitmap as its own page.
- Detects Eighth Edition bitmap headers and decodes their run-length format.
- Optionally undoes Eighth Edition scanline XOR on the host or leaves it for the printer.
- Encodes raster data into a compact pattern/count format for a PostScript `bitmap` procedure.
- Supports page selection, copies, forms per page, orientation, offsets, magnification, accounting, and arbitrary PostScript passthrough.

Input/control flow:
- `bitmap()` loops over all bitmaps returned by `dimensions()`, emits page setup, reads compressed raster records through `addrast()`, emits scanlines with `putrast()`, and closes the page.
- `dimensions()` distinguishes V8 bitfiles by an initial zero word, reads origin/corner coordinates or direct scanline/pattern counts, allocates `raster` and `prevrast`, and initializes the previous raster to all ones.
- `addrast()` expands input pattern runs into the current raster line.
- `putrast()` optionally XOR-reconstructs V8 rasters, then emits repeated or literal hex chunks.
- `patncmp()` detects repeated `bytespp`-sized patterns.
- `getint()` reads little-endian 16-bit words.

Important behavior:
- `bytespp <= 0` disables normal repeated-pattern chunking by using whole scanlines as a pattern size.
- `flip` is passed to the PostScript prologue rather than applied in C.
- Bounding box comments are computed from the maximum bitmap width and height seen.
- Page count increments only for pages actually sent to stdout by `redirect()`.

Dependencies:
- Shared common headers and routines: `comments.h`, `gen.h`, `path.h`, `ext.h`, `cat()`, `out_list()`, `in_olist()`, `setencoding()`, `writerequest()`, `saverequest()`, `error()`, `interrupt()`.
- Expects prologue procedures `setup`, `pagesetup`, `bitmap`, and `done`.

Risks and quirks:
- `addrast()` does not bounds-check `rptr` against `eptr`; malformed input can overflow the raster buffer.
- EOF handling in raster expansion can leave partially filled buffers before later format checks.
- `dimensions()` frees/reallocates buffers for each bitmap but does not reset all global format state except what it reads.
- Uses `char` buffers for binary raster data and masks on output, which works for emission but is signedness-sensitive in comparisons.
