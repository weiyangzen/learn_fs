# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmiff.c

## Role

MIFF file-format printer device for 24-bit direct-color output.

## Exported Device

- `gs_miff24_device`, named `miff24`, 24-bit RGB, 72 DPI default.

## Main Flow

`miff24_print_page`:

1. Allocates one raster line.
2. Writes MIFF textual metadata: ImageMagick id, DirectClass, columns, RunlengthEncoded compression, rows, and delimiter.
3. Iterates scan lines with `gdev_prn_get_bits`.
4. Emits RLE tuples as RGB bytes plus count byte, where count is additional repeats up to 255.
5. Frees the line buffer and returns the accumulated code.

## Dependencies

Uses `gdevprn.h` printer-device raster access.

## Risks and Edge Cases

- The RLE count is “extra matching pixels,” not total run length.
- If writing to `FILE *` fails, individual `putc` calls are not checked.
- No filesystem-specific logic beyond writing stream bytes to the configured output.
