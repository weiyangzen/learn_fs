# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/gzspotan.c

Implements the spot analyzer device used for spot topology analysis and TrueType-style vertical stem recognition.

Key behavior:
- Defines GC descriptors for the analyzer device, trapezoid records, and trapezoid contact records.
- Implements freelist/buffer management for trapezoids and contacts, with hard caps around 10000 allocations per buffer type.
- Provides cyclic-list helpers for Y-band trapezoid lists and contact lists.
- Defines a minimal Ghostscript device descriptor named `spot analyzer`; most device procs are null except open, close, clipping box, fill path, and copy finalization hooks.
- `san_open` initializes buffers and x-extents; `san_close` frees buffers.
- `gx_san__obtain` allocates/opens the device and uses a lock count; `gx_san__release` decrements and releases when no longer used.
- `gx_san_begin` resets current topology state and reuses existing buffers through freelists.
- `gx_san_trap_store` accepts trapezoids in increasing Y-band and X order, builds upper/lower contact topology, tracks leftmost/rightmost boundaries, and updates global x extents.
- `try_unite_last_trap` merges adjacent prolongation trapezoids when topology and outline boundaries match.
- Stem detection uses trapezoid area/axis length to estimate average width and rejects nearly horizontal boundaries using tangent/cosine checks.
- Hint generation has two modes internally: by selecting representative trapezoid width or by selecting outline tangents; the active path uses tangent-based hints.
- Overall hints identify leftmost/rightmost outer glyph boundaries when requested.
- Stem hints follow single-descendent/single-ancestor contiguous trapezoid chains and call a client handler with `gx_san_sect`.
- Visual tracing hooks draw trapezoids, contacts, stems, and hints when enabled.

Research notes:
- The implementation assumes the trapezoid fill algorithm emits trapezoids in a strict scanning order.
- GC comments note that only buffer links are valid during collection; topology work pointers are transient.
