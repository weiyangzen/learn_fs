# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevlj56.c

Implements HP LaserJet 5/6 PCL XL printer devices: `lj5mono` and `lj5gray`.

Key behavior:
- Registers `gs_lj5mono_device` as 1-bit monochrome and `gs_lj5gray_device` as 8-bit grayscale.
- `ljet5_open` opens the Ghostscript printer and writes a PCL XL file header through stream helpers.
- `ljet5_close` writes the PCL XL trailer and closes the printer.
- `ljet5_print_page` writes a PCL XL page header, media selection, color-space setup, image header, and then one compressed image block per scan line.
- Monochrome output uses an indexed 1-bit palette; grayscale output uses direct 8-bit gray pixels.
- Each line is compressed with `gdev_pcl_mode2compress_padded`.
- Uses PCL XL token helpers from `gdevpx*.h`.

Dependencies and notes:
- Includes `stream.h`, `gdevpcl.h`, and PCL XL attribute/operator headers.
- `MIN_SKIP_LINES` is defined but not used; this implementation sends the whole image one line at a time.
- Allocates a padded word buffer for scanning and a separate output compression buffer.
