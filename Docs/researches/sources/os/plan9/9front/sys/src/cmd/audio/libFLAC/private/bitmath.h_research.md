# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/bitmath.h

## Role

`private/bitmath.h` provides inline bit-counting utilities used throughout codec parsing and coding-cost logic. It covers count-leading-zero operations, integer log2, wide log2, and declares signed integer log2.

## Major Functions

- `FLAC__clz_soft_uint32()` uses a 256-entry table to count leading zeroes in a 32-bit word.
- `FLAC__clz_uint32()` and `FLAC__clz_uint64()` select compiler intrinsics or software fallbacks.
- `FLAC__clz2_uint32()` and `FLAC__clz2_uint64()` are zero-safe wrappers.
- `FLAC__bitmath_ilog2()` computes floor log2 for 32-bit values.
- `FLAC__bitmath_ilog2_wide()` computes floor log2 for 64-bit values, using intrinsics or a de Bruijn fallback.
- `FLAC__bitmath_silog2()` is declared for signed magnitude bit-width calculations.

## Important Implementation Details

The non-`clz2` helpers assert that input is nonzero. GCC/Clang builtins are used when available; MSVC and Intel paths use bit-scan intrinsics. The de Bruijn fallback normalizes the 64-bit value to the next power form and indexes a static table.

## Risks / Edge Cases

- Calling `FLAC__clz_uint32()`, `FLAC__clz_uint64()`, or log2 helpers with zero violates asserted preconditions.
- Compiler feature paths must match the platform's builtin semantics; builtins for zero input are intentionally avoided.
- `FLAC__bitmath_ilog2_wide()` relies on correct `FLAC__U64L()` macro definition from `share/compat.h`.

## Dependencies

Uses `FLAC/ordinals.h`, `FLAC/assert.h`, `share/compat.h`, and optional MSVC intrinsics.
