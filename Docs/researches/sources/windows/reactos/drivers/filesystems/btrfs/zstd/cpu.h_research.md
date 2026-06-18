# File Research: sources/windows/reactos/drivers/filesystems/btrfs/zstd/cpu.h

## Purpose

Runtime CPU feature detection helper used by Zstd, especially for BMI2-aware decompression/compression paths.

## Main Components

- `ZSTD_cpuid_t` stores CPUID feature registers:
  - `f1c`
  - `f1d`
  - `f7b`
  - `f7c`
- `ZSTD_cpuid()` gathers CPUID feature bits through:
  - MSVC `__cpuid` / `__cpuidex`
  - GCC inline assembly
  - special 32-bit PIC `ebx` save/restore handling
- Generated feature-test helpers include:
  - SSE/SSE2/SSE3/SSSE3/SSE4
  - AVX/AVX2/AVX512 variants
  - BMI1/BMI2
  - POPCNT, AES, PCLMUL, FMA
  - ADX, SHA, CLWB, and related x86 flags.

## Dependencies

- `<string.h>`
- `mem.h`
- `<intrin.h>` on MSVC.

## Consumers

- `zstd_decompress.c` uses `ZSTD_cpuid_bmi2(ZSTD_cpuid())` to initialize BMI2 capability in the decompression context.

## Research Notes

- Non-x86 builds return zeroed feature fields.
- The generated `ZSTD_cpuid_<feature>()` functions are inline/static via `MEM_STATIC`.
- Correct `ebx` preservation is important for 32-bit PIC builds.
