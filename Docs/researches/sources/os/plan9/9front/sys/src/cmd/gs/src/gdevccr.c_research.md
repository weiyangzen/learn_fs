# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevccr.c

## Purpose
Implements a CalComp Raster Format printer/output driver named `ccr`.

## Device
- `gs_ccr_device`: A3-sized, 300 dpi, 3-component, 8-bit-depth printer device with 0.2 inch margins.

## Color Mapping
- `ccr_map_rgb_color` reduces RGB to 1-bit-per-component CMY by thresholding the top bit and inverting RGB to CMY.
- `ccr_map_color_rgb` converts packed CMY bits back to full-intensity RGB.

## Output Behavior
- `ccr_print_page` reads every rendered scan line, unpacks pixels into C/M/Y bit bytes, stores all rows in memory, and then writes separate Y, M, and C passes.
- The output stream is wrapped with CalComp control bytes:
  - file start
  - new pass separators
  - line start records
  - empty-line records
  - file end

## Internal Data
`cmyrow` stores per-row buffers and effective lengths for each color pass. Helper routines allocate row buffers, append packed CMY bytes, write each pass, and free allocated memory.

## Dependencies
Uses Ghostscript printer helpers from `gdevprn.h`.

## Notes
- The driver buffers the entire page in memory before writing passes, so memory cost scales with page height and width.
- Allocation failure paths free already allocated line buffers.
