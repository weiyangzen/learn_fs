# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevccr.c

Ghostscript CalComp Raster Format output driver.

Key behavior:
- Defines one `ccr` device, defaulting to 300 DPI A3-sized output with 0.2 inch margins and 3 one-bit CMY components.
- Custom RGB-to-color mapping converts RGB to a 3-bit CMY bitmap.
- `ccr_print_page` allocates a row buffer for every page row plus per-row C/M/Y buffers, converts each rendered input byte group into packed C, M, and Y pass data, then writes the output as three passes: Y, M, C.
- CalComp output commands include file start/end, new pass, empty line, and line-start-with-length markers.
- Helper routines allocate/free row buffers, append packed CMY bytes while tracking effective nonzero length, and write each color pass.

Notable dependencies:
- Uses Ghostscript printer APIs from `gdevprn.h`.

Research notes:
- The implementation stores all page rows before writing passes, so memory usage scales with page height and width rather than streaming one row at a time.
- `alloc_line` allocates each plane buffer with `cols` bytes even though packed output advances one byte per 8 pixels, overallocating by roughly 8x but simplifying allocation.
- The color decode routine appears to place red/blue values in reversed indexes relative to the usual `rgb[0]`, `rgb[1]`, `rgb[2]` convention; this may be harmless if rarely used, but it is suspicious.
