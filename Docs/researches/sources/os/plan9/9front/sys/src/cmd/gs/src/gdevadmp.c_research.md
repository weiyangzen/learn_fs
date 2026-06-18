# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevadmp.c

## Scope

Apple Dot Matrix Printer and ImageWriter family driver.

## Key Behavior

- Defines devices `appledmp`, `iwlo`, `iwhi`, and `iwlq` with different horizontal/vertical resolutions.
- `dmp_print_page` chooses a device mode from resolution, initializes the printer, and processes the page in 8-, 16-, or 24-scanline groups.
- Copies scanlines in reversed vertical order for printer bit ordering, transposes 8x8 blocks, and packs data differently for DMP/IW low, IW high, and ImageWriter LQ.
- Trims leading/trailing blank data and emits printer commands for skips and graphics data.
- Applies ImageWriter end-of-page workaround before formfeed/reset.

## Dependencies

Uses Ghostscript printer helpers and transposition routines from `gdevprn.h`.

## Risks And Invariants

- Different device modes use different pass counts and packing layout.
- The ImageWriter paper-position workaround is printer-behavior-specific.
- Allocation cleanup must free three large buffers on error and success.
