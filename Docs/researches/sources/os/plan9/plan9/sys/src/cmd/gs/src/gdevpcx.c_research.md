# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpcx.c

This file implements Ghostscript PCX output devices. It provides monochrome, grayscale, EGA/VGA 16-color, 256-color fixed-palette, 24-bit, and 4-bit CMYK PCX variants.

Device descriptors include `gs_pcxmono_device`, `gs_pcxgray_device`, `gs_pcx16_device`, `gs_pcx256_device`, `gs_pcx24b_device`, and `gs_pcxcmyk_device`. Most use `prn_color_procs`; the CMYK variant provides explicit CMYK mapping through `cmyk_1bit_map_*`. Shared PC color helpers from `gdevpccm.c` are used for EGA/VGA and 8-bit palette modes.

The file defines the 128-byte PCX header layout in `pcx_header`, including manufacturer, version, RLE encoding flag, bits-per-pixel per plane, extents, resolution, 16-color palette, number of planes, bytes-per-line, and palette interpretation. `assign_ushort` handles the little-endian PCX header fields across host endian variants. A DCX header format is documented but not implemented.

Each print routine prepares a header and delegates to `pcx_write_page`: `pcxmono_print_page` writes a bilevel palette, `pcx16_print_page` writes an EGA palette and planar data, `pcx256_print_page` writes an 8-bit image followed by a 256-entry palette, `pcx24b_print_page` writes three 8-bit planes, and `pcxcmyk_print_page` writes a custom CMYK palette.

`pcx_write_page` fills header fields, writes the header, then iterates printer rows through `gdev_prn_get_bits`. Non-planar data is padded to even byte length and RLE encoded directly. Planar depth 4 data is split into four bit planes; depth 24 data is emitted as separate R/G/B planes. `pcx_write_rle` performs PCX run-length encoding, limiting runs to 15 bytes for compatibility with fragile readers.
