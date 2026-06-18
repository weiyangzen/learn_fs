# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math.c

## Purpose
Coordinates RAID-Z parity math implementations. It registers compiled backends, selects a backend at runtime, benchmarks supported implementations in kernel builds, exposes generation/reconstruction dispatch, and supports user selection by implementation name.

## Implementations
- `vdev_raidz_original_impl` is an opaque placeholder for the original scalar code in `vdev_raidz.c`; its NULL methods tell callers to use the original implementation.
- `vdev_raidz_scalar_impl` is always present when supported.
- On amd64, SSE2, SSSE3, and AVX2 implementations are included.
- `vdev_raidz_fastest_impl` is populated with the fastest method per generation/reconstruction function.

## Selection State
- `zfs_vdev_raidz_impl` is the active selector. Values include `fastest`, `cycle`, `original`, `scalar`, or an index into supported implementations.
- `user_sel_impl` records a user preference set before math initialization.
- `raidz_supp_impl[]` stores supported implementations after probing.
- `raidz_math_initialized` gates selectors that require benchmark/probe completion.

## Key Functions
- `vdev_raidz_math_get_ops()` returns scalar ops if FPU/SIMD is not allowed in the current context. Otherwise it returns fastest, cycles through supported impls, original, scalar, or an indexed supported implementation.
- `vdev_raidz_math_generate()` selects P, PQ, or PQR generation function from `rm_ops`; NULL means use original implementation.
- `vdev_raidz_math_reconstruct()` chooses a reconstruction function based on parity level, which parity columns are valid, and the number of bad data columns. Unsupported cases return `RAIDZ_ORIGINAL_IMPL`.
- `benchmark_raidz()` probes each implementation, calls optional init hooks, stores supported ops, and either benchmarks each method in kernel or picks the last supported implementation in user space to avoid zdb/zhack/zinject/ztest overhead.
- `benchmark_raidz_impl()` measures per-disk throughput for each method and records the best implementation for each function slot.
- `vdev_raidz_math_init()` benchmarks/probes and atomically applies the user selector.
- `vdev_raidz_impl_set()` sanitizes a requested name, accepts mandatory options (`cycle`, `fastest`, `original`, `scalar`) or initialized supported implementation names, then updates the active or pending selector.

## Important Behavior And Invariants
- SIMD backends are only used when `kfpu_allowed()` permits FPU use; otherwise scalar is selected regardless of the configured implementation.
- The fastest implementation is per-method, not necessarily a single backend for every parity operation.
- In user space, benchmarking is skipped deliberately; this changes selection behavior for libzpool consumers.
- Linux-only module parameter glue is present under `defined(_KERNEL) && defined(__linux__)`, but the illumos port comments note OpenZFS-style free-form kstats are omitted here.

## Dependencies
Uses RAID-Z implementation ops, ABD-backed synthetic zios/maps for benchmarks, SIMD/FPU availability helpers, GF method names, and kernel parameter support where available.
