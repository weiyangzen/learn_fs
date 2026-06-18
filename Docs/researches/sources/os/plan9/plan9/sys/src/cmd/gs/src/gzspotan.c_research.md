# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gzspotan.c

Implements the spot analyzer device used for glyph topology analysis and stem recognition, primarily for TrueType grid fitting and antialiased rendering support.

Main flow:
- Defines a mostly-null device procedure table, using `gx_default_fill_path` and a custom unlimited clipping box.
- Allocates reusable linked buffers for trapezoids and trapezoid contacts, with hard caps around 10000 entries.
- `gx_san__obtain` / `gx_san__release` manage a ref-counted analyzer device.
- `gx_san_begin` resets active band/contact state while reusing allocated buffers.
- `gx_san_trap_store` consumes trapezoids in increasing Y-band and X order, reconstructs upper/lower contacts, merges prolongations, and tracks glyph x extents.
- Stem generation walks the reconstructed topology, recognizes vertical-ish boundaries, computes area/axis-derived average width, and emits `gx_san_sect` hints through a caller handler.

Notable implementation details:
- Cyclic lists model bands and contact sets.
- Visual tracing hooks (`vd_*`) draw traps, contacts, stems, and hints under tracing.
- The algorithm assumes ordered trapezoid input from the fill pipeline.
- `gx_san_end` is currently empty.

This is graphics/glyph analysis code. It is memory-management sensitive because GC descriptors only consider buffer links valid during GC.
