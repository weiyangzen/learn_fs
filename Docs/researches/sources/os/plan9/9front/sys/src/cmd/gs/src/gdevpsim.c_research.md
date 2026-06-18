# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpsim.c

This file implements bitmap-only PostScript output devices:
- `psmono`: 1-bit monochrome Level 1 PostScript.
- `psgray`: 8-bit grayscale using the same Level 1 path.
- `psrgb`: 24-bit RGB Level 2 PostScript.

Shared logic:
- `ps_image_write_headers` writes the DSC file header once per output file using `gdevpsu.c` helpers, computes a page bounding box from printer dimensions/resolution, emits device-specific setup procedures, and writes each page header.

`psmono`/`psgray`:
- Device descriptors are `gs_psmono_device` and `gs_psgray_device`.
- `psmono_setup` defines PostScript procedures for decoding a custom compact run-length/hex image stream.
- `psmono_print_page` reads each scanline with `gdev_prn_get_bits`, detects repeated byte runs of at least 10 bytes, emits repeat-run codes, and sends other bytes via `write_data_run`.
- `write_data_run` writes compact count codes followed by hexadecimal data, optionally inverting bytes for 1-bit output.
- `psmono_close` writes the final DSC trailer through `psw_end_file`.

`psrgb`:
- Device descriptor is `gs_psrgb_device`.
- `psrgb_setup` defines a `rgbimage` PostScript procedure using `ASCII85Decode` and `RunLengthDecode`.
- `psrgb_print_page` builds Ghostscript stream filters `RunLengthEncode -> ASCII85Encode -> file`, writes planar R, G, B data per scanline, then emits the page trailer.
- `psrgb_close` writes the final DSC trailer.

Filesystem relevance is limited to writing printer output through `FILE *` and Ghostscript printer-device abstractions. The file does not implement storage logic.
