# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpjet.c

Ghostscript drivers for HP PaintJet, PaintJet XL, and DEC LJ250 printers.

Key behavior:
- Defines three printer devices: `lj250`, `paintjet`, and `pjetxl`.
- Uses `180x180` dpi, 3-bit PCL color mapping, and PaintJet/PCL page emission.
- `lj250_print_page` enters PCL emulation, terminates raster graphics for setup, then prints through common logic and exits PCL emulation.
- `paintjet_print_page` sends PaintJet setup and uses the common page path.
- `pjetxl_print_page` resets with `ESC E`, applies a different vertical origin, and uses the common page path.
- `pj_common_print_page` allocates scanline and plane buffers, configures raster resolution, line width, color planes, origin, compression mode, and raster start.
- For each scanline, copies printer memory, trims trailing zeros, accumulates blank-line skips, pads to an 8-byte boundary, transposes chunky 3-bit pixel data into separate R/G/B bit planes, and sends compressed rows.
- Emits color planes in R, G, B order, using PCL transfer commands with plane suffixes.
- `compress1_row` performs simple run-length compression where each run is encoded as count byte plus complemented data byte, splitting long runs.

Research notes:
- This is legacy printer output code and uses PCL/PaintJet command sequences.
- It is unrelated to the pdfwrite font/text files except for sharing Ghostscript printer-device infrastructure.
