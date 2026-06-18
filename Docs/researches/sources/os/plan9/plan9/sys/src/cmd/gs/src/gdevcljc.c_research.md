# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevcljc.c

Ghostscript H-P Color LaserJet 5/5M contone driver, based on the CLJ driver but hardwired for 24-bit direct RGB output.

Key responsibilities:
- Defines the `cljet5c` printer device at 300 dpi, 24-bit RGB.
- Allocates raw scanline, compressed scanline, and previous-row buffers.
- Emits PCL reset, paper definition, transparency controls, render mode, resolution, direct-by-pixel RGB color model, raster start, and compression mode 3 setup.
- Copies each rendered scanline, compresses it with PCL mode 3 against the previous row, and writes it to the printer.
- Ends raster graphics and ejects the page.

Important behavior:
- Color parameters, render mode, and bits per component are hardwired.
- Uses direct RGB with 8 bits per component through `\033*v6W`.
- Compression seed row starts as zeroed `prow`.

Dependencies:
- Ghostscript printer and PCL support: `gdevprn.h`, `gdevpcl.h`.
- Uses default RGB color mapping procs.

Notable risks:
- The previous-row buffer passed to `gdev_pcl_mode3compress` is initialized but not visibly updated in this function; correctness depends on that compression helper updating or interpreting it as seed state.
- Several PCL positioning and margin constants are hard-coded.
- The device is simpler than `gdevclj.c` and lacks the paper/resolution validation logic found there.
