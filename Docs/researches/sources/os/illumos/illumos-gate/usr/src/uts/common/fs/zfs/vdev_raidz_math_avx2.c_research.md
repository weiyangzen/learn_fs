# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/vdev_raidz_math_avx2.c

## Purpose
Provides the amd64 AVX2 RAID-Z math backend. It defines vector-register helper macros for GF(2^8) operations, includes the generic RAID-Z math template, generates AVX2 parity/reconstruction methods, and registers support probing.

## Main Components
- amd64-only implementation guarded by `#if defined(__amd64)`.
- Inline assembly macros for YMM loads, stores, XOR, copy, zero, multiply-by-2, multiply-by-4, and table-based multiplication.
- FPU scope macros `raidz_math_begin()` and `raidz_math_end()` wrap `kfpu_begin()`, `vzeroupper`, and `kfpu_end()`.
- Stride/register mapping macros define how the shared `vdev_raidz_math_impl.h` template emits AVX2 variants for generation, syndrome, and reconstruction functions.
- `DEFINE_GEN_METHODS(avx2)` and `DEFINE_REC_METHODS(avx2)` instantiate method arrays.

## Key Operations
- `XOR_ACC`, `XOR`, `ZERO`, `COPY`, `LOAD`, and `STORE` operate on 32-byte YMM lanes, typically in two- or four-register groups.
- `MUL2_SETUP()` prepares constants for GF multiply-by-2; `MUL2` and `MUL4` apply field multiplication with AVX2 byte operations.
- `MUL(c, ...)` uses lookup tables from `gf_clmul_mod_lt` and byte shuffles to multiply by arbitrary GF constants.
- `raidz_will_avx2_work()` requires FPU use to be allowed and CPU AVX plus AVX2 availability.

## Registered Ops
`vdev_raidz_avx2_impl` has generated `.gen` and `.rec` method arrays, no init/fini hooks, support callback `raidz_will_avx2_work`, and name `avx2`.

## 32-bit Stub
For `__i386`, the file exposes a stub `vdev_raidz_avx2_impl` with NULL method pointers and name `avx2`, satisfying user-level fakekernel dependencies without providing AVX2 operations.

## Important Behavior And Invariants
- Assembly paths assume aligned 32-byte vector operations through the template and ABD/method setup.
- `vzeroupper` is issued before leaving the AVX2 math scope to avoid AVX/SSE transition penalties and preserve kernel FPU hygiene.
- Unsupported contexts must be filtered by the math dispatcher or support predicate; direct use requires FPU/SIMD safety.
