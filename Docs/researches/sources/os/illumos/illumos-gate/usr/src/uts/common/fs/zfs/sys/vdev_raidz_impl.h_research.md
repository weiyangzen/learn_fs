# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/vdev_raidz_impl.h

This private header defines RAID-Z parity/reconstruction operation tables, map/column structures, implementation wrappers, kstats, and Galois-field helpers.

Core definitions:
- Parity code indexes `CODE_P`, `CODE_Q`, `CODE_R`; parity widths `PARITY_P`, `PARITY_PQ`, `PARITY_PQR`; reconstruction targets `TARGET_X/Y/Z`.
- `raidz_math_gen_op` and `raidz_rec_op` enumerate parity generation and reconstruction methods.
- `raidz_impl_ops_t` contains init/fini, generation function array, reconstruction function array, support predicate, and implementation name.
- `raidz_col_t` stores child index, offset, size, ABD, known-good copy, error, tried, and skipped state.
- `raidz_map_t` stores column counts, size/asize, missing counts, first data column, skip/padding information, ABD copy, report/freed/injected flags, selected ops, and flexible column array.
- Implementation symbols include scalar and x86 SSE2/SSSE3/AVX2 ops when built for x86.
- Wrapper macros generate implementation-specific dispatch functions and ops-array initializers.
- `raidz_impl_kstat_t` reports generation/reconstruction speeds.
- `raidz_mul_info_t` indexes multiplication constants needed by reconstruction formulas.

Galois-field helpers:
- Extern aligned pow/log tables map GF(2^8) exponent/log values.
- Inline `vdev_raidz_exp2()`, `gf_mul()`, `gf_div()`, `gf_inv()`, `gf_exp2()`, and `gf_exp4()` implement field arithmetic.

Risk-sensitive invariants:
- Reconstruction math assumes nonzero divisors where asserted and wraps exponents modulo 255.
- SIMD implementation selection must use `is_supported()` before dispatch.
- `raidz_map_t` is variable-sized with one trailing column and must be allocated by the RAID-Z map allocator.
