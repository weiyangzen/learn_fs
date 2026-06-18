# File Research: sources/os/plan9/9front/sys/src/cmd/audio/libFLAC/cpu.c

## Purpose

This file populates `FLAC__CPUInfo` with runtime CPU capability data. libFLAC uses that data to choose assembly or intrinsic-optimized code paths when available.

## x86 Detection

For IA-32 and x86-64 builds with NASM or x86 intrinsics enabled and assembly not disabled, the file defines CPUID feature masks for CMOV, MMX, SSE, SSE2, SSE3, SSSE3, SSE4.1, SSE4.2, OSXSAVE, AVX, FMA, and AVX2.

Helper functions:

- `cpu_xgetbv_x86()` reads XCR0 to verify OS AVX register support.
- `cpu_have_cpuid()` detects CPUID availability through architecture assumptions, NASM helper, GCC `cpuid.h`, or MSVC inline assembly.
- `cpuinfo_x86()` wraps CPUID leaf queries across MSVC, GCC, and NASM paths.
- `x86_cpu_info()` sets `use_asm`, detects Intel vendor string, fills feature booleans, emits debug logging when assertions are enabled, and disables AVX/AVX2/FMA if the OS does not save YMM state.

## PowerPC Detection

`ppc_cpu_info()` detects PowerPC ISA capability for `arch_2_07` and `arch_3_00` via Linux `getauxval(AT_HWCAP2)`, FreeBSD `elf_aux_info()`, or hard-coded false values on Apple. Other PowerPC platforms intentionally hit a compile-time unsupported-platform error.

## Public Entry Point

`FLAC__cpu_info(FLAC__CPUInfo *info)` zeroes the structure, sets the CPU type based on compile-time macros, and dispatches to x86, PowerPC, or a default no-assembly path.

## Integration Points

The file depends on `private/cpu.h`, `share/compat.h`, and platform headers such as `<cpuid.h>`, `<intrin.h>`, or `<sys/auxv.h>` when enabled. The information produced here is consumed by optimized LPC, fixed predictor, bit operations, and other libFLAC routines selected elsewhere.

## Risks and Notes

Feature detection combines compile-time capability with runtime OS support. AVX advertised by CPUID is deliberately cleared unless OSXSAVE and XCR0 indicate the OS can preserve AVX state. On 9front builds, many platform-specific branches may compile out, leaving `use_asm = false`; that is a valid conservative result.
