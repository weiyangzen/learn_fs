# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmacpictop.h

Macro library for serializing Classic MacOS QuickDraw PICT opcodes and data structures into a memory buffer.

Key contents:
- Low-level write macros for bytes, 16-bit ints, 32-bit longs, fill bytes, and opcodes.
- QuickDraw structure writers for points, rectangles, regions, patterns, RGB colors, color specs, color tables, and PixMaps.
- `PICTWriteDataPackBits` writes raw bitmap data for small rasters or calls QuickDraw `PackBits` per row for larger rasters, including per-row byte counts and even-byte padding.
- Text writer macros handle Pascal strings and padding.
- Defines many PICT opcode macros:
  - Clipping, patterns, text state, colors, highlight/op colors.
  - Lines and text drawing.
  - Font names.
  - Rectangles, rounded rectangles, ovals, arcs, and same-shape variants.
  - BitsRect and PackBitsRect bitmap/pixmap forms.
  - End-picture opcodes.
- Provides Ghostscript-to-PICT color helpers:
  - `GSSetStdCol`
  - `GSSetFgCol`
  - `GSSetBkCol`

Dependencies and notes:
- Includes `<QDOffscreen.h>`.
- This is macro-only code and mutates the supplied pointer argument extensively.
- Several macros depend on ambient variable names, notably `raster` inside `PICTWriteDataPackBits`; callers must match those assumptions.
- Some rarely used macros appear fragile, for example `PICTWriteRegion` parameter naming and `PICT_PnSize` argument forwarding.
