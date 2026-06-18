# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevpcx.c

## Purpose

`gdevpcx.c` implements Ghostscript printer devices that write PCX image files in monochrome, grayscale, 16-color planar, 8-bit palette, 24-bit planar RGB, and 4-bit chunky CMYK-like forms.

## Devices

The exported devices are `gs_pcxmono_device`, `gs_pcxgray_device`, `gs_pcx16_device`, `gs_pcx256_device`, `gs_pcx24b_device`, and `gs_pcxcmyk_device`. They use Ghostscript printer-device macros with appropriate color mapping: default mono/gray mappings, PC 4-bit/8-bit palette mapping from `gdevpccm`, default RGB mapping, or 1-bit CMYK mapping.

## PCX Header and Palettes

The file defines `pcx_header`, matching the 128-byte PCX header layout with little-endian 16-bit fields. `assign_ushort` swaps bytes on big-endian hosts. A prototype header supplies common defaults. The file also defines EGA and CMYK palette tables. A DCX header format is documented but not used.

Each print-page routine fills the variable header fields for its format: PCX version, bits per pixel per plane, plane count, palette info, and palette bytes. `pcx256_print_page` writes a trailing 256-entry palette marker and palette data after image data.

## Output Flow

`pcx_write_page` is the shared writer. It allocates a row buffer, fills header dimensions/resolution/bytes-per-line, writes the 128-byte header, iterates rows with `gdev_prn_get_bits`, and encodes each row with PCX RLE.

For non-planar output, it writes the row directly, padding odd byte counts as required by PCX. For 4-bit planar output, it converts chunky nibbles into four 1-bit planes. For 24-bit output, it emits separate R, G, and B planes by stepping through chunky RGB data.

`pcx_write_rle` writes line data using PCX run-length encoding. It limits run counts to 15 even though the format allows 63, for compatibility with readers that mishandle larger runs. Literal bytes with high bits set are escaped.

## Dependencies

The file uses `gdevprn.h`, `gdevpccm.h`, and luminance/color mapping support. It shares palette-writing with `pc_write_palette`.

## Filesystem Relevance

It writes PCX bytes to Ghostscript-managed `FILE *` streams. It does not implement filesystem logic.

## Risks and Notes

The RLE routine reads `*from` after advancing `from` before testing `from == end`, which relies on the caller's row buffer layout and may be fragile at exact row ends. Planar conversion assumes input depth 4 or 24 for planar paths; other depths return rangecheck. PCX little-endian header assignment is handled manually.
