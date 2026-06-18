# File Research: sources/virtualization/nbdkit/filters/swab/swab.c

This filter presents the same export with fixed-width byte swapping applied to data. `swab-bits` accepts 8, 16, 32, or 64 bits; 8 effectively disables transformation. Export size is rounded down to the swap width, and block-size constraints are adjusted so clients are told to use at least that alignment.

All data-bearing or range-bearing operations require count and offset alignment to `bits/8`, returning `EINVAL` otherwise. Reads forward to the underlying plugin and then swap in place. Writes allocate a temporary block, byte-swap into it, and write transformed bytes to the underlying layer. Trim, zero, extents, and cache validate alignment and either forward directly or use `nbdkit_extents_aligned`.

Risks and invariants: the filter relies on strict alignment to avoid partial element transformations. Write allocation is per request and can fail with the caller-visible errno. The code casts buffers to 16/32/64-bit pointer types after alignment validation, so callers must not bypass the advertised constraints.
