# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevdjtc.c

Ghostscript HP DeskJet 500C color PCL driver.

Key behavior:
- Defines `djet500c` as a 300x300 DPI, 3-bit RGB-style printer device with PCL 3-bit color mapping.
- Uses compile-time `SHINGLING` and `DEPLETION` settings for DeskJet color print quality behavior.
- `djet500c_print_page` resets/configures the printer, selects RGB raster mode, depletion, shingling, mode-2 compression, and raster start.
- For each scanline, reads packed 3-bit pixel data, skips blank lines, pads line data, transposes R/G/B bits into separate planes, complements plane bits for printer semantics, compresses each plane, and emits PCL raster-transfer commands.
- `mode2compress` implements HP mode 2 run/literal compression for arbitrary line lengths.

Notable dependencies:
- Ghostscript printer and PCL APIs: `gdevprn.h`, `gdevpcl.h`.
- Uses C library `malloc`/`free` rather than Ghostscript memory allocators for its work buffers.

Research notes:
- This is contributed legacy driver code.
- Allocation failures are not checked after `malloc` for `bitData` or plane buffers; null dereferences are possible under memory pressure.
- The compressor reads `*exam` in loop tests where `exam` may have reached `end_row`, so edge-case out-of-bounds reads are plausible.
