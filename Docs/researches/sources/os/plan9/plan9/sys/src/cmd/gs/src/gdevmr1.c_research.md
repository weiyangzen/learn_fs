# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/gdevmr1.c

RasterOp implementation for monobit memory devices.

- Main entry point is `mem_mono_strip_copy_rop`.
- Converts Ghostscript logical operations to effective 1-bit ROP3 with transparency handling through `gs_transparent_rop`.
- Lazily initializes the mono palette if needed, then adjusts ROP semantics when device bit polarity is inverted.
- Simplifies operations based on source and texture palettes, including known-0, known-1, inverted-source, and inverted-texture cases.
- Fast-paths constant fills, no-ops, copy-mono-compatible source operations, and strip-tile-compatible texture operations.
- General path walks destination rows and tiled texture spans, fetches skewed source/texture bytes, applies `rop_proc_table[rop]`, and masks edge bytes.
- Includes debug tracing/dump hooks under `DEBUG`.
- Risk notes: this is bit-level code with multiple skew/mask calculations; correctness depends on prior clipping via `fit_fill`/`fit_copy` and valid texture repetition metadata.
