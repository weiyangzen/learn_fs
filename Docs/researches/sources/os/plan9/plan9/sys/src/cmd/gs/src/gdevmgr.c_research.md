# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmgr.c

MGR bitmap output driver for Ghostscript printer devices.

- Defines `gx_device_mgr`, extending `gx_device_printer` with `mgr_depth`.
- Registers devices: `mgrmono`, `mgrgray2`, `mgrgray4`, `mgrgray8`, `mgr4`, and `mgr8`.
- Uses standard printer open/output/close procs, with custom print-page functions for monochrome, gray, and color MGR output.
- `mgr_begin_page` writes an MGR bitmap header using `B_PUTHDR8`, allocates a row buffer, and initializes a cursor.
- `mgr_print_page` outputs 1-bit rows padded to byte boundaries.
- `mgrN_print_page` repacks Ghostscript 8-bit gray scan lines into 2-, 4-, or 8-bit MGR gray formats, builds gray CLUT entries, and byte-swaps CLUT words on little-endian hosts.
- `cmgrN_print_page` handles 4-bit PC color and 8-bit MGR color; the 8-bit path remaps a 7x7x4 cube plus reserved colors into an MGR CLUT.
- `mgr_8bit_map_rgb_color` and `mgr_8bit_map_color_rgb` implement the fixed MGR 8-bit color mapping with extra gray shades.
- Risk notes: page routines allocate temporary buffers and return immediately on some write errors, so cleanup is not always symmetrical. Static CLUT and mapping tables make the driver non-reentrant.
