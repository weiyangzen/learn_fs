# sources/storage-engines/foundationdb/flow/rte_memcpy.h

## Purpose
`rte_memcpy.h` vendors a DPDK-derived optimized memcpy implementation for x86 Linux/FreeBSD builds with AVX enabled. It provides `rte_memcpy` and `rte_rdtsc` helpers using SSE, AVX2, or AVX512 intrinsics for high-throughput non-overlapping memory copies.

## Important APIs, Types, And Functions
The main public helper is `static force_inline void* rte_memcpy(void* dst, const void* src, size_t n)`. Internal helpers include `rte_mov16`, `rte_mov32`, `rte_mov64`, `rte_mov128`, `rte_mov256`, `rte_mov128blocks`, `rte_mov512blocks` in AVX512 mode, `rte_memcpy_generic`, `rte_memcpy_aligned`, unaligned SSE macros `MOVEUNALIGNED_LEFT47_IMM` and `MOVEUNALIGNED_LEFT47`, and `rte_rdtsc`. Compile-time feature macros set `RTE_MACHINE_CPUFLAG_AVX512F` or `RTE_MACHINE_CPUFLAG_AVX2` and `ALIGNMENT_MASK`.

## Control Flow
The file is active only when building on Linux or FreeBSD with `__AVX__`; otherwise it contributes no implementation. `rte_memcpy` checks whether source and destination meet the selected alignment mask and dispatches to aligned or generic copy. Each architecture path handles small sizes with overlapping front/back vector moves, medium sizes with fixed unrolled blocks, and large sizes by aligning destination stores then copying repeated 128/256/512-byte blocks before copying the tail. SSE fallback uses `_mm_alignr_epi8` switch macros to make unaligned loads with immediate offsets efficient.

## State And Persistence
There is no mutable persistent state. All state is CPU register, stack, and pointer arithmetic inside a single call. `rte_rdtsc` reads the processor timestamp counter and returns it without synchronization or persistence.

## Dependencies And Integration Points
The header depends on `<stdint.h>`, `<stdio.h>`, `<string.h>`, Flow `Platform.h` for `force_inline`, and x86 intrinsic availability implied by the compiler target. It is intended as an internal fast-copy primitive for Flow or FoundationDB hot paths that can guarantee memcpy semantics rather than memmove semantics.

## Risks
The source and destination must not overlap; overlapping copies can corrupt data. The code is selected by compile-time flags, so binaries built with AVX2 or AVX512 instructions must not run on CPUs lacking those features unless the broader build uses runtime dispatch. Small-copy paths use typed unaligned integer stores that can trigger strict-aliasing or sanitizer concerns depending on compiler settings. Large-copy alignment logic intentionally reads around vector boundaries and assumes valid ranges described by the algorithm. `rte_rdtsc` is not serialized and is not portable across cores or frequency behavior.

## Test Signals
Correctness tests should compare `rte_memcpy` with libc `memcpy` for sizes 0 through several kilobytes, all source/destination alignments, and page-boundary-adjacent buffers. Sanitizer builds, CPU-feature-specific CI lanes, and non-overlap assertions in callers are important. Performance benchmarks can validate that the header is actually beneficial versus the platform libc for FoundationDB workloads.
