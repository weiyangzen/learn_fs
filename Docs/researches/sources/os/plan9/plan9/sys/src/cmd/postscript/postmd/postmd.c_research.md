# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/postmd/postmd.c

Matrix-display translator that renders floating-point matrices as PostScript grayscale images.

Key responsibilities:
- Emits PostScript job structure and copies the `POSTMD` prologue.
- Reads one matrix per input file, optionally with a header.
- Maps matrix elements through an interval list into grayscale byte values.
- Supports custom grayscale/color maps, matrix dimensions, display windows, labels, statistics, page requests, forms per page, accounting, and arbitrary PostScript passthrough.
- Encodes each displayed row using the same repeated-pattern hex format used by bitmap translators.

Input/header support:
- Matrix headers can define:
  - `dimension`
  - `interval`
  - `colormap` or `grayscale`
  - `window`
  - `name`
  - `statistics`
- If stdin is used, `copystdin()` copies it to a temp file so header probing and seeking work.
- If dimensions are absent, `dimensions()` counts all remaining elements and assumes a square matrix using `sqrt(count)`.

Control flow:
- `matrix()` resets defaults, builds interval/color/window state, reads the optional header, validates dimensions/window, starts a page, maps matrix elements into row raster data, emits rows, labels the matrix, and closes the page.
- `buildilist()` constructs alternating less-than/equality interval regions and default grayscale values.
- `addcolormap()` overrides region colors.
- `setwindow()`, `inwindow()`, and `inrange()` select a submatrix.
- `mapfloat()` classifies each element and increments per-region counts.
- `putrow()` compresses row bytes into repeated/literal hex chunks.
- `labelmatrix()` emits PostScript calls for title, window labels, interval labels, counts, and legend.

Important behavior:
- Default interval list is `-1,0,1`, producing seven regions.
- Region colors default from near-white to black.
- `nxtstat` can suppress legend counts for the next matrix while still printing the legend structure.
- `bytespp <= 0` disables normal repeated-pattern chunking by using the row width.
- Temporary stdin copy is unlinked in `done()`.

Dependencies:
- Shared common layer: `comments.h`, `gen.h`, `path.h`, `ext.h`, `cat()`, `out_list()`, `in_olist()`, `setencoding()`, `writerequest()`, `saverequest()`, `error()`, `interrupt()`, `tempnam()`.
- Local interval structures from `postmd.h`.
- Links with math library for `sqrt()`.

Risks and quirks:
- `fscanf(fp_in, "%f", &element)` uses a `double element`; modern C expects `%lf` for `double *`.
- `rows = sqrt(count)` truncates silently and does not verify the element count is a perfect square.
- `setwindow()` writes coordinates without checking more than four tokens.
- `addcolormap()` can write beyond `ilist[]` if too many colors are supplied.
- Matrix labels are inserted into PostScript strings without escaping parentheses/backslashes.
- Uses tempnam-style temporary file creation.
