# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevatx.c

## Scope

Practical Automation ATX-23, ATX-24, and ATX-38 printer driver.

## Key Behavior

- Defines three printer devices with model-specific page widths, DPI, and margins.
- Emits ATX commands for page length, vertical tab, uncompressed data, compressed data, and end page.
- `atx_compress` encodes even-byte scanline data as repeated-pair compressed segments or literal pair segments.
- `atx_print_page` computes capped page height, enforces minimum page length, skips blank lines, truncates to model maximum width, compresses when beneficial, and writes page data.
- Per-model print functions call common output with maximum byte widths.

## Dependencies

Uses Ghostscript printer APIs, allocation helpers, `math_.h` for `ceil`, and raster access helpers.

## Risks And Invariants

- Compressed data command has a one-byte word count, so compressed scanlines are capped at 510 bytes.
- Input and output compression sizes are assumed even.
- Comments note margin handling is conceptually wrong because coordinates are treated as printable-area coordinates.
