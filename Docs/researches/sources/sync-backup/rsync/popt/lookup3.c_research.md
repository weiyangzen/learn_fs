
<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/rsync/popt/lookup3.c -->
# Research: sources/sync-backup/rsync/popt/lookup3.c

## Purpose
`popt/lookup3.c` provides Bob Jenkins lookup3 32-bit hash functions for hash table lookup, with optional single-hash, pair-hash, word-array, byte-array, big-endian, and self-test builds. In this rsync tree it supports popt bitset/Bloom-filter-style helpers through `poptJlu32lpair()`.

## Important APIs, Types, and Functions
- Endian detection uses static union `endian` and macros `HASH_LITTLE_ENDIAN`/`HASH_BIG_ENDIAN`.
- Mixing macros `_JLU3_INIT`, `_JLU3_MIX(a,b,c)`, and `_JLU3_FINAL(a,b,c)` implement the Jenkins reversible block mix and final avalanche.
- Conditionally compiled functions: `jlu32w()`, `jlu32l()`, `jlu32lpair()`, and `jlu32b()`.
- `_JLU3_SELFTEST` enables test drivers `driver1()` through `driver4()` and a `main()`.

## Control Flow
Each hash initializes `a`, `b`, and `c` from `0xdeadbeef + size + seed`, then processes 12-byte/3-word blocks through `_JLU3_MIX()`. Tail handling is specialized by endian and alignment: aligned little-endian can read 32-bit chunks, half-aligned little-endian reads 16-bit chunks, and unaligned or other cases assemble bytes. `jlu32lpair()` also incorporates a secondary seed in `c` and returns two results through `pc` and `pb`. Big-endian `jlu32b()` mirrors the strategy for big-endian ordering.

## State and Persistence
The functions are pure except for output parameters in `jlu32lpair()`. No global mutable state is used. The self-test build prints diagnostics and returns from a local `main()`.

## Dependencies and Integration Points
It depends on `<stdint.h>` and compile-time feature macros selecting which symbols are emitted. `popt.c` uses the pair hash via popt's wrapper names for bitset operations. It is non-cryptographic and intended for lookup distribution, not security.

## Risks
Fast aligned tail paths intentionally read beyond the nominal byte length and mask unused bytes; this is documented as safe on common word-boundary memory systems but noisy under Valgrind unless `VALGRIND` is defined. Endian/alignment assumptions are delicate on strict-alignment platforms. The hash must not be used as an adversarial security primitive. A visible typo in the `VALGRIND` branch of `jlu32l()` (`a+=k[0] break`) would matter if that compile path is enabled.

## Test Signals
Build with default, `VALGRIND`, and `_JLU3_SELFTEST` configurations. Run the self-test drivers for avalanche, alignment, overread, and zero-length behavior. Cross-platform tests should compare expected hashes on little-endian, big-endian, aligned, and unaligned buffers.
<!-- END_FILE_RESEARCH: sources/sync-backup/rsync/popt/lookup3.c -->
