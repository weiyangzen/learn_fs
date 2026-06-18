# sources/storage-engines/foundationdb/fdbrpc/libeio/ecb.h

## Purpose

`ecb.h` is the bundled libecb compatibility header used by `libeio`. It provides compiler/architecture feature detection, memory fences, inline/attribute macros, branch prediction hints, bit operations, byte swapping, endian tests, and arithmetic helpers.

## Important APIs, types, and functions

The file defines fixed-width integer typedefs on Windows, `ECB_GCC_VERSION()`, `ECB_MEMORY_FENCE` and acquire/release variants, `ecb_inline`, `ecb_restrict`, `ecb_attribute()`, `ecb_expect()`, `ecb_likely()`, `ecb_unlikely()`, bit helpers `ecb_ctz32/64`, `ecb_popcount32/64`, `ecb_ld32/64`, rotation helpers, `ecb_bswap16/32/64`, `ecb_unreachable()`, `ecb_assume()`, endian helpers `ecb_big_endian()` and `ecb_little_endian()`, `ecb_mod()`, division rounding macros, and `ecb_array_length()`.

## Control flow, state, and persistence

Most functionality is inline or macro-only. If no architecture/compiler fence is available and pthread fallback is allowed, it declares a static `pthread_mutex_t ecb_mf_lock` used by `ECB_MEMORY_FENCE`, which is process-local state. Otherwise the header has no persistent state.

## Dependencies and integration points

`eio.c` includes this header for `ecb_inline`, `ecb_noinline`, `ecb_cold`, branch prediction, endian-aware sorting, and other low-level helpers. The fence macros may pull in pthreads, but FoundationDB builds `eio` as a static C library and links it into `fdbrpc` when bundled `libeio` is compiled.

## Risks and test signals

This old compatibility header uses architecture-specific assembly and compiler-version heuristics. Incorrect fence selection can cause queue visibility bugs on weak memory models; incorrect bit/endian helpers can affect directory entry sorting. Test signals are clean `eio` compilation on the target compiler, thread sanitizer runs around request queues, and readdir ordering tests on large directories.
