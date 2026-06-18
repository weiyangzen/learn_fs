# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevsj48.c

Ghostscript monochrome printer driver for the StarJet SJ48.

Key behavior:
- Defines the `sj48` printer device as an 8 x 10.5 inch monochrome page at 360x360 DPI.
- Supports only 180 or 360 DPI in each axis; unsupported resolutions return `rangecheck`.
- Selects ESC graphics mode based on x/y resolution: 39, 40, 71, or 72.
- Allocates input scanline and transposed output buffers.
- Skips blank scanlines and emits vertical motion using `ESC J`, constrained to 1/180-inch units.
- Transposes raster data in 8-scanline blocks with `gdev_prn_transpose_8x8`.
- Emits graphics with `ESC *`, alternating horizontal skips and nonblank graphics runs.
- Aligns the final print pass so the bottom of the 48-jet head reaches the bottom margin.
- Ends pages with form feed and flushes the stream.

Notable dependencies:
- Ghostscript printer helpers from `gdevprn.h`, especially scanline copy and 8x8 transpose helpers.

Research notes:
- Comments note derivation from Canon BJ10/BJ200 code and uncertainty about margin details for StarJet.
- The implementation has careful bottom-margin logic because only part of the physical head is used.
- This is printer raster output code, not filesystem code.
