## sources/security-integrity/attr/libmisc/high_water_alloc.c

Purpose: reusable growing-buffer allocator.

`high_water_alloc` reallocates only when requested size exceeds current capacity, rounding up to 256-byte chunks and updating caller pointers. State is caller-owned buffer pointer and size. Dependencies are `realloc`. Risks include returning `1` while preserving the old buffer, integer rounding assumptions, and no shrink behavior. Tests are indirect through long line/value/encoding paths in attr tools.
