# Research: sources/storage-engines/rocksdb/port/lang.h

## Purpose
This header defines small language/compiler compatibility utilities used across RocksDB. It hides compiler-specific attributes for fallthrough, sanitizer annotations, static object lifetime policy, debug assertions, and compile-time CPU feature macros.

## Important APIs, Types, And Functions
`FALLTHROUGH_INTENDED` maps to `[[clang::fallthrough]]`, `[[gnu::fallthrough]]`, or a no-op statement. `DECLARE_DEFAULT_MOVES(Name)` declares defaulted noexcept move construction and move assignment. `STATIC_AVOID_DESTRUCTION(Type, name)` either creates a normal static object under ASAN/Valgrind or a leaked heap-backed static reference in production. `kMustFreeHeapAllocations` records which mode is active.

`TSAN_SUPPRESSION` maps to `__attribute__((no_sanitize("thread")))` when thread sanitizer is detected. `DEBUG_FAIL(msg)` expands to an assertion failure with a grouping message. `ASSERT_FEATURE_COMPAT_HEADER()` is a static assertion sentinel. The header also normalizes `__SSE4_2__`, `__PCLMUL__`, and `__POPCNT__` based on `__AVX__`, `NO_PCLMUL`, and `NO_POPCNT`.

## Control Flow
All behavior is selected by preprocessor checks. ASAN is detected through clang `__has_feature(address_sanitizer)` or GCC `__SANITIZE_ADDRESS__`; Valgrind runs force the same heap-freeing mode. TSAN detection is normalized so clang feature detection defines the GCC-style `__SANITIZE_THREAD__` macro before `TSAN_SUPPRESSION` is chosen.

## State And Persistence Behavior
No runtime persistence is present. The most important state effect is static object lifetime: production builds intentionally avoid non-trivial static destruction by leaking heap-allocated singletons, while sanitizer/Valgrind builds use true static objects so leak detectors and heap cleanup can observe destructors.

## Dependencies And Integration Points
The header integrates with many RocksDB files that need portable annotations, singleton/static registries, sanitizer-specific behavior, or CPU feature gates for optimized code. It depends only on compiler and build-system macros.

## Risks And Edge Cases
`STATIC_AVOID_DESTRUCTION` intentionally trades leak reports for destruction-order safety in production-like builds. Any code relying on static destructors will behave differently under sanitizer and non-sanitizer builds. CPU feature inference from `__AVX__` is a compatibility convenience, not runtime CPU detection, so it must only be used for compile-time guarded code paths. `DEBUG_FAIL` depends on `assert`, so behavior changes under `NDEBUG`.

## Test Signals
Signals are mostly build-matrix based: clang, GCC, MSVC-like macro environments, ASAN, TSAN, Valgrind, and feature-disabled builds. Runtime tests indirectly validate static registries and optimized code compiled under the normalized CPU feature macros.
