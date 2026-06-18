# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevpsim.c

This file implements bitmap-only PostScript printer devices:
- `psmono`: 1-bit monochrome Level 1 PostScript.
- `psgray`: 8-bit grayscale Level 1 PostScript using the same encoder.
- `psrgb`: 24-bit RGB Level 2 PostScript.

Shared setup is handled by `ps_image_write_headers`, which writes the DSC file header on first use, computes a page bounding box from printer dimensions/resolution, emits device-specific setup procedures, and writes each page header through the `gdevpsu.c` helpers.

`psmono`/`psgray` path:
- Device descriptors are `gs_psmono_device` and `gs_psgray_device`.
- `psmono_setup` defines PostScript procedures for decoding a custom compact run-length/hex image stream.
- `psmono_print_page` reads each scanline with `gdev_prn_get_bits`, detects repeated-byte runs of at least 10 bytes, emits repeat-run codes, and sends literal data through `write_data_run`.
- `write_data_run` writes count codes and hexadecimal data, optionally inverting bytes for 1-bit output.
- `psmono_close` writes the final DSC trailer with `psw_end_file`.

`psrgb` path:
- Device descriptor is `gs_psrgb_device`.
- `psrgb_setup` defines an `rgbimage` PostScript procedure using `ASCII85Decode` and `RunLengthDecode`.
- `psrgb_print_page` builds Ghostscript stream filters `RunLengthEncode -> ASCII85Encode -> file`, writes planar R, G, and B data for every scanline, closes filters, and emits the page trailer.
- `psrgb_close` writes the final DSC trailer.

Filesystem relevance is limited to writing printer output through `FILE *` and Ghostscript printer abstractions. The code is an output device, not storage or VFS logic.
