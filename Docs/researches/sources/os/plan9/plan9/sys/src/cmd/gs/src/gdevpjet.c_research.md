# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpjet.c

## Role

`gdevpjet.c` implements Ghostscript printer drivers for HP PaintJet, PaintJet XL, and DEC LJ250 color printers.

## Devices

- `gs_lj250_device`
- `gs_paintjet_device`
- `gs_pjetxl_device`

All use 3-bit PCL color mapping, 8.5x11 defaults, 180 dpi, and a common print routine with device-specific setup/end strings and vertical origin.

## Print Flow

- `lj250_print_page()` enters and exits PCL emulation mode around common printing.
- `paintjet_print_page()` emits PaintJet raster setup and form feed.
- `pjetxl_print_page()` resets the XL and uses a different vertical origin.
- `pj_common_print_page()` allocates scanline and plane buffers, emits PCL raster setup, walks scanlines, skips blank lines by vertical movement, transposes chunky color pixels into RGB planes, compresses each plane row, and writes raster transfer commands.
- `compress1_row()` performs PaintJet run-length compression and complements bytes because the image was accumulated in complemented form.

## Dependencies

Uses Ghostscript printer APIs, PCL color mapping helpers from `gdevpcl.h`, scanline copy/raster helpers, `FILE` output, and Ghostscript memory allocation.

## Risks And Invariants

- `X_DPI` and `Y_DPI` must match and be either 90 or 180 per the source comment.
- `LINE_SIZE` is rounded to an 8-byte multiple because transposition operates in 8-byte blocks.
- Buffer allocation handles partial allocation cleanup.
- Compression worst case can double row size, and the temporary compression buffer is sized accordingly.
