# sources/test-tools/stress-ng/test/test-icc-mm_stream_si64.c

## Purpose

This file checks compiler and target support for vector/SIMD constructs such as `_mm_stream_si64`. It gives the configuration step a concrete compile test before enabling architecture-specific accelerated stress-ng code.

## Important APIs, Types, and Functions

Headers: `immintrin.h`. Defined functions: `main`. Referenced calls/builtins: `_mm_stream_si64`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `_mm_stream_si64`; the program returns `(int)val` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `immintrin.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_ICC_MM_STREAM_SI64 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 37 lines.

- Probe category: SIMD/intrinsic availability probe.

- Includes: immintrin.h.

- Calls/builtins detected: _mm_stream_si64.

- Structs/types detected: none.
