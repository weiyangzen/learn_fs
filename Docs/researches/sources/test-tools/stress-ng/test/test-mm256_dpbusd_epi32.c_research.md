# sources/test-tools/stress-ng/test/test-mm256_dpbusd_epi32.c

## Purpose

This file checks compiler and target support for vector/SIMD constructs such as `rndset, __attribute__, target, _mm256_dpbusd_epi32`. It gives the configuration step a concrete compile test before enabling architecture-specific accelerated stress-ng code.

## Important APIs, Types, and Functions

Headers: `immintrin.h`, `string.h`, `stdint.h`. Defined functions: `rndset`, `target`. Referenced calls/builtins: `rndset`, `__attribute__`, `target`, `_mm256_dpbusd_epi32`. Important scalar/library types: `size_t`, `uintptr_t`.

## Control Flow

Control flow is deliberately linear: helper function(s) `rndset`, `target` initialize data or provide callbacks; one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; `main` invokes `rndset`, `__attribute__`, `target`, `_mm256_dpbusd_epi32`; the program returns `*(int *)&r` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `immintrin.h`, `string.h`, `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: SIMD probes depend on target attributes, headers, alignment, and compiler ISA support.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MM256_DPBUSD_EPI32 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 42 lines.

- Probe category: SIMD/intrinsic availability probe.

- Includes: immintrin.h, string.h, stdint.h.

- Calls/builtins detected: rndset, __attribute__, target, _mm256_dpbusd_epi32.

- Structs/types detected: size_t, uintptr_t.
