# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gxcolor2.h

Internal Level 2 color support definitions.

Key contents:
- Defines `gs_indexed_map`, a reference-counted cache for Indexed color procedure values or Separation tint-transform values.
- Declares `lookup_indexed_map`, `alloc_indexed_map`, and `free_indexed_map`.
- Defines `gs_pattern1_instance_t` for PatternType 1 instances.
- Pattern instance stores template data, tiling-to-device step matrix, tiling-space bounding box, simple/uses-mask flags, device size, and cached bitmap ID.
- Provides private structure descriptor macros for indexed maps and pattern instances.

Notable dependencies:
- Client color definitions, matrices, reference counting, and bitmap IDs.

Research notes:
- `gxclrast.c` uses the indexed map declarations when reconstructing Indexed color spaces during clist playback.
- The pattern portion documents Ghostscript’s adjusted “tiling space” model for efficient tile-copy coverage.
