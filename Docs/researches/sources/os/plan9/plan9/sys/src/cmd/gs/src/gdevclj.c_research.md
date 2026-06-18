# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevclj.c

Ghostscript H-P Color LaserJet 5/5M driver using a 3-plane bi-level color model.

Key responsibilities:
- Defines `cljet5` and `cljet5pr` devices.
- Validates supported paper sizes and resolutions.
- Supplies supported `InputAttributes` page sizes.
- Computes default matrices for normal and rotated page output.
- Packs byte-per-pixel 3-bit color data into separate C/M/Y bit planes.
- Compresses each plane with PCL mode 2 compression.
- Emits PCL setup, raster dimensions, blank-line skips, compressed plane data, raster end, and form feed.
- Provides a special `cljet5pr` variant that performs driver-level page rotation for PCL interpreters that cannot use `setpagedevice`.

Important behavior:
- Only executive, letter, and A4 color page sizes are listed.
- Supported resolutions are 75, 100, 150, and 300 dpi, and X/Y resolution must match.
- `USE_FAST_MODE` selects the faster fixed/simple color-space path; alternate direct color mode is present in comments/conditional command emission.
- `clj_put_params` rejects unknown media sizes and rotated media for the standard driver.
- `clj_pr_put_params` can synthesize a rotated `.MediaSize` parameter list and mark the device rotated, explicitly violating the usual device invariant as documented in the comments.
- `pack_and_compress_scanline` trims trailing zero longwords from each plane before compression.

Dependencies:
- Ghostscript printer and PCL support: `gdevprn.h`, `gdevpcl.h`, parameter APIs, C parameter lists, and PCL color mappers.
- Uses `fabs` from `math_.h`.

Notable risks:
- The driver-level rotation variant mutates page size/width/height during get/put parameter paths and is intended only for specific PCL interpreter contexts.
- `clj_media_size` can use `fres.data` while only `HWSize` was supplied; if `HWResolution` was not read successfully in that path, the resolution source is fragile.
- Buffer sizing depends on `CLJ_MAX_SCANLINE` and the supported media/resolution assumptions.
- Only a narrow set of page sizes is accepted for color output.
