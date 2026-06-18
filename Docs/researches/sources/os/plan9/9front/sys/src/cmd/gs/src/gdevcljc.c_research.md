# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevcljc.c

Ghostscript contone HP Color LaserJet 5/5M driver based on `gdevclj.c`, but with hardwired 24-bit direct RGB output.

Key behavior:
- Defines `gs_cljet5c_device` as a 300 DPI, 24-bit RGB printer device.
- `cljc_print_page` allocates raw, compressed, and previous-row buffers.
- Emits PCL reset, paper definition, color render mode, direct RGB pixel format, raster setup, and mode 3 compression selection.
- For each scanline, copies rendered data and sends PCL mode 3 delta-compressed raster data against the previous row.
- Ends raster graphics and ejects the page.

Notable dependencies:
- Ghostscript printer and PCL compression APIs.

Research notes:
- Color encoding and render mode are intentionally hardwired.
- Compared with `gdevclj.c`, this is smaller and simpler but sends full contone raster data rather than bitplane-packed YMC.
