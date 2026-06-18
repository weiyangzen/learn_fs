# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmr1.c

## Role

RasterOp implementation for monobit memory devices.

## Main Function

- `mem_mono_strip_copy_rop` applies Ghostscript RasterOp logic to 1-bit destination memory.

## Main Behavior

- Computes effective RasterOp with `gs_transparent_rop`.
- Ensures the monobit palette is initialized and detects inverted black/white semantics.
- Adjusts RasterOp for inverted device bit meaning by reversing/inverting rop bits.
- Special-cases operations that reduce to fill, no-op, copy-mono, or strip-tile.
- Handles source and texture palettes by rewriting or simplifying the RasterOp.
- Falls back to a byte-level loop that combines destination, source, and texture bytes with `rop_proc_table`.
- Handles tile phase and repeated texture offsets with `x_offset`.

## Dependencies

Uses Ghostscript RasterOp tables and macros from `gsropt.h`, `gxdevrop.h`, and `gdevmrop.h`.

## Risks and Edge Cases

- The routine is optimized around bit alignment, masks, and skews; off-by-one behavior depends on prior `fit_copy`/`fit_fill`.
- Source/texture pointers may be dummy values in special cases; validity is protected by setup decisions.
- Debug paths can dump initial and final bitmaps.
