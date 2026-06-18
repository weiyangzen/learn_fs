# Research: sources/storage-engines/rocksdb/port/likely.h

## Purpose
This tiny portability header provides branch prediction macros for hot code paths. It preserves LevelDB-style `LIKELY` and `UNLIKELY` names while using compiler intrinsics when available.

## Important APIs, Types, And Functions
`LIKELY(x)` expands to `__builtin_expect((x), 1)` on GCC-compatible compilers version 4 or newer, and `UNLIKELY(x)` expands to `__builtin_expect((x), 0)`. On other compilers both macros evaluate to the expression itself.

## Control Flow
There is no runtime control flow beyond expression evaluation. The macro result is used by the compiler to bias branch layout and prediction metadata. The fallback preserves semantics without optimization hints.

## State And Persistence Behavior
No state is stored and no persistent behavior exists. The only effect is generated code shape in branches where callers apply the macros.

## Dependencies And Integration Points
The header depends on `__GNUC__` version macros. It is included by performance-sensitive RocksDB code that wants portable branch hints without depending directly on compiler builtins.

## Risks And Edge Cases
Arguments are still evaluated exactly once because the macros wrap the expression once. Misusing branch hints can hurt performance by biasing layout incorrectly, but it should not change correctness. Non-GCC compilers receive no hint unless they also define compatible GCC macros.

## Test Signals
There is typically no direct unit test. Compile coverage across supported compilers and performance tests on hot paths are the meaningful signals.
