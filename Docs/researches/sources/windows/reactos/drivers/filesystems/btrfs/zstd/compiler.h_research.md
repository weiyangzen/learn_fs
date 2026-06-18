# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/compiler.h

## Purpose

Compiler abstraction header for the imported Zstd code. It centralizes inline/noinline attributes, target attributes, BMI2 dispatch configuration, prefetch helpers, vectorization suppression, branch prediction macros, and MSVC warning controls.

## Main Components

- Inlining:
  - `INLINE_KEYWORD`
  - `FORCE_INLINE_ATTR`
  - `FORCE_INLINE_TEMPLATE`
  - `HINT_INLINE`
  - `UNUSED_ATTR`
  - `FORCE_NOINLINE`
- Target and dispatch:
  - `TARGET_ATTRIBUTE`
  - `DYNAMIC_BMI2`
- Prefetch:
  - `PREFETCH_L1`
  - `PREFETCH_L2`
  - `PREFETCH_AREA`
  - `CACHELINE_SIZE`
- Optimization hints:
  - `DONT_VECTORIZE`
  - `LIKELY`
  - `UNLIKELY`
- MSVC pragmas disabling common portability warnings.

## Dependencies

- May include `<mmintrin.h>` for MSVC x86/x64 prefetch.
- Uses compiler predefined macros for GCC, Clang, ICCARM, MSVC, x86, and AArch64.

## Research Notes

- `DYNAMIC_BMI2` enables runtime BMI2-specialized paths when supported by compiler/target and BMI2 is not already globally enabled.
- This file affects generated code throughout Zstd/FSE/HUF but contains no runtime codec logic.
- Incorrect compiler macro changes can alter ABI visibility, inlining, CPU dispatch, or kernel build compatibility.
