# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevclj.c

Ghostscript HP Color LaserJet 5/5M PCL driver, plus a page-rotation variant.

Key behavior:
- Defines `gx_device_clj` with standard printer state and a `rotated` flag.
- Supports 75, 100, 150, and 300 DPI square resolutions.
- Supports specific color-capable media sizes via `clj_paper_sizes`, with logical long-edge-feed orientation metadata and offsets.
- `clj_get_initial_matrix` builds the page matrix according to media orientation and rotation.
- `clj_get_params` publishes supported input media sizes.
- `clj_put_params` validates requested page size and resolution, rejecting unsupported or rotated media in the standard device.
- `pack_and_compress_scanline` converts 3-bit-per-pixel YMC byte data into C/M/Y bit planes and compresses each plane using PCL mode 2.
- `clj_print_page` emits PCL setup, scans imageable rows, skips blank lines, writes C/M/Y compressed planes, and ends the raster/page.
- `cljet5pr` variant fakes rotation by rewriting `.MediaSize` before delegating to printer parameters.

Notable dependencies:
- Ghostscript printer and PCL APIs: `gdevprn.h`, `gdevpcl.h`.
- Parameter APIs for synthesized page-size lists.

Research notes:
- The file documents a hardware tradeoff between fast fixed color modes and more accurate direct color mode; `USE_FAST_MODE` is enabled.
- The rotation variant explicitly breaks a usual Ghostscript device invariant by modifying parameters, and the comments restrict its intended use to PCL interpreter contexts lacking proper `setpagedevice`.
