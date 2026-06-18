# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/private/cpu.h

## Role

`private/cpu.h` defines CPU architecture detection macros, compiler intrinsic support macros, target attributes, and the `FLAC__CPUInfo` structures used to select optimized codec routines.

## Major Contents

- Detects x86_64 and IA32 from compiler predefined macros.
- Defines `FLAC__SSE_TARGET()` and `FLAC__FAST_MATH_TARGET()` for compilers with target attributes.
- Sets support macros for SSE, SSE2, SSSE3, SSE4.1, AVX, AVX2, and FMA depending on compiler and `FLAC__USE_AVX`.
- Defines CPU info enums and structures for x86 and PowerPC capabilities.
- Declares `FLAC__cpu_info()` plus IA32 CPUID assembly helpers.

## Important Implementation Details

The header separates compile-time support for intrinsics from runtime CPU feature detection. Runtime selection uses `FLAC__CPUInfo`, while the compile-time macros decide which optimized functions can be compiled and declared elsewhere.

## Risks / Edge Cases

- Feature availability depends on build-system macros such as `FLAC__HAS_X86INTRIN`, `FLAC__USE_AVX`, and compiler version.
- MSVC, GCC, Clang, and Intel compiler branches differ in target attribute support.
- On non-x86 builds most SIMD macros remain undefined or zero and generic C paths are expected.

## Dependencies

Includes `FLAC/ordinals.h` and optionally `config.h`.
