# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmgr.c

## Role

MGR bitmap output device driver. It converts Ghostscript printer-page rasters into MGR saved-bitmap format for mono, grayscale, and color variants.

## Exported Devices

- `gs_mgrmono_device`
- `gs_mgrgray2_device`
- `gs_mgrgray4_device`
- `gs_mgrgray8_device`
- `gs_mgr4_device`
- `gs_mgr8_device`

## Main Flow

- `mgr_begin_page` writes an MGR `b_header`, allocates a row buffer, and initializes a cursor.
- `mgr_next_row` reads Ghostscript printer scan lines into the cursor buffer and frees it at end.
- `mgr_print_page` writes 1-bit rows.
- `mgrN_print_page` converts 8-bit Ghostscript grayscale rows into 2/4/8-bit MGR grayscale packing and appends a color lookup table.
- `cmgrN_print_page` converts 4-bit and 8-bit color rows into MGR color packing and emits lookup-table entries.
- `mgr_8bit_map_rgb_color` and `mgr_8bit_map_color_rgb` implement MGR’s 7x7x4 color cube plus extra grays.
- `clut2mgr` scales table values into MGR lookup values; `swap_bwords` endian-swaps 16-bit fields on little-endian hosts.

## Dependencies

Uses `gdevprn.h` printer raster APIs, `gdevpccm.h` PC palette helpers, and `gdevmgr.h` MGR header/palette definitions.

## Risks and Edge Cases

- Several allocation failure paths return without freeing already allocated cursor memory.
- Output code mutates row buffers in the 8-bit paths.
- The 8-bit color palette reserves `MGR_RESERVEDCOLORS` before emitted dynamic entries.
