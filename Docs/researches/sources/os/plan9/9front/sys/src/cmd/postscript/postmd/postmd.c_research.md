# File Research: sources/os/plan9/9front/sys/src/cmd/postscript/postmd/postmd.c

`postmd.c` is a matrix display program that maps floating-point matrix data to grayscale PostScript images.

Main flow:
- Standard translator sequence: signals, DSC header/prologue, options, setup, arguments, done, accounting.
- `matrix()` processes one matrix per input file, with optional header metadata.
- If reading stdin, `copystdin()` writes it to a temporary file so the code can seek while discovering headers/dimensions.
- `getheader()` recognizes `dimension`, `window`, `name`, `colormap`/`grayscale`, `interval`, and `statistics`.
- `dimensions()` resolves matrix rows/columns, inferring square dimensions from element count if needed, allocates a raster row, and validates/reset window coordinates.
- Matrix elements are scanned with `fscanf("%f", &element)`, windowed, mapped to grayscale bytes, encoded row by row, and then labeled.

Mapping:
- `buildilist()` builds an interval list from comma/slash/space-separated floating values.
- The interval list partitions real values into `2n+1` regions.
- `addcolormap()` overrides default grayscale assignments.
- `mapfloat()` maps each element to a grayscale byte and updates per-region statistics.
- `labelmatrix()` emits labels and legend data, optionally zeroing stats if disabled.

Output:
- Emits `columns rows bitmap` call for the displayed window.
- `putrow()` uses the same pattern/repeat hex encoding style as `postdmd`.
- `labelmatrix()` calls prologue procedures for title, window coordinates, and legend.

Options:
- Pattern bytes, copies, default dimensions, grayscale/colormap, interval list, magnification, forms per page, page list, orientation, window, offsets, accounting, copy-through, encoding, prologue, pass-through PostScript, requests, debug, ignore-fatal.

Risks:
- Uses `tempnam()`, which is historically race-prone.
- `fscanf("%f", &element)` passes a `double *` to `%f`; modern C expects `float *` for `%f` and `double *` for `%lf`, making this legacy code fragile/undefined under strict modern compilation.
- Header parsing is prefix-based with `strncmp()` against keyword lengths, so abbreviated prefixes can match.
- Fixed `ilist[128]` can overflow if an excessive interval list is supplied.
- `matrixname` from headers can contain newline text and is written into a PostScript string without the same escaping discipline as data bytes.

Filesystem relevance: only temporary/input file handling; no filesystem implementation.
