# sources/test-tools/stress-ng/test/test-libbsd.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_BSD` and link flags `-lbsd` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `string.h`, `stdlib.h`, `bsd/stdlib.h`. Defined functions: `defined`, `main`. Referenced calls/builtins: `intcmp`, `memset`, `heapsort`, `mergesort`, `radixsort`.

## Control Flow

Control flow is deliberately linear: helper function(s) `defined` initialize data or provide callbacks; conditional compilation or simple runtime branches select the available platform path; `main` invokes `intcmp`, `memset`, `heapsort`, `mergesort`, `radixsort`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `string.h`, `stdlib.h`, `bsd/stdlib.h`; linker availability for `-lbsd`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_BSD`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 54 lines.

- Probe category: external library/header link probe.

- Includes: string.h, stdlib.h, bsd/stdlib.h.

- Calls/builtins detected: intcmp, memset, heapsort, mergesort, radixsort.

- Structs/types detected: none.
