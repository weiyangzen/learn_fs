# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/share/alloc.h

## Role

`share/alloc.h` provides shared safe allocation helpers for libFLAC and related tools. It avoids zero-byte allocation ambiguity, checks arithmetic overflow for allocation sizes, and includes fuzzing hooks for allocation-failure testing.

## Major Helpers

- `safe_malloc_()` and `safe_calloc_()` convert zero-size requests to at least one byte.
- `safe_malloc_add_*()` check additive overflow.
- `safe_malloc_mul_2op_()` is declared externally; `safe_malloc_mul_3op_()`, `safe_malloc_mul2add_()`, and `safe_malloc_muladd2_()` check multiplication or combined multiplication/addition.
- `safe_realloc_()` wraps realloc and frees the old pointer on nonzero-size failure.
- `_nofree_` realloc variants preserve the old pointer on failure.
- Multiplication realloc helpers either free on overflow/failure or preserve depending on the `_nofree_` name.
- Fuzzing mode can force allocation failures through global counters.

## Important Implementation Details

The header defines `SIZE_MAX` if missing, with MSVC-specific fallbacks. It distinguishes POSIX `realloc(ptr, 0)` semantics in realloc helpers from libFLAC's safe malloc convention of never requesting zero bytes.

## Risks / Edge Cases

- `safe_realloc_()` and several non-`nofree` helpers free the old pointer on failure; callers must not assume old storage remains valid.
- Some zero-size paths intentionally call `malloc(1)`, while realloc zero-size paths preserve POSIX free-like behavior.
- Fuzzing hooks are compiled only under `FUZZING_BUILD_MODE_UNSAFE_FOR_PRODUCTION`.

## Dependencies

Includes `limits.h`, optional `stdint.h`, `stdlib.h`, and `share/compat.h`.
