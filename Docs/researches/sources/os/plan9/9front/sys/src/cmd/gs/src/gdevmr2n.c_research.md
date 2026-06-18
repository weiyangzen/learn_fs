# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gdevmr2n.c

## Role

RasterOp support for 2-bit and 4-bit gray memory devices, implemented as a “fake” monobit expansion where possible.

## Main Function

- `mem_gray_strip_copy_rop`

## Main Behavior

- Rejects complex cases to `mem_default_strip_copy_rop`: color devices, transparency, non-solid source palettes, or non-solid texture palettes.
- For supported gray cases, rewrites source and texture colors into 1-bit-equivalent values.
- Scales coordinates and tile dimensions by `log2_depth`.
- Temporarily patches `fill_rectangle`, `copy_mono`, and `strip_tile_rectangle` to stub routines that return failure if the monobit implementation tries to use shortcuts.
- Calls `mem_mono_strip_copy_rop` over widened bit coordinates.
- Falls back to the default RasterOp implementation if the monobit path punts.

## Research Notes

This file deliberately trades completeness for reuse. It provides a fast path only for cases that can be safely represented as monobit operations over expanded coordinates.
