# sources/test-tools/stress-ng/test/test-float.c

## Purpose

This file is a portable configure probe for `NEED_GNUC, __attribute__, optimize, float_ops`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `math.h`, `../core-version.h`. Local macros: `OPTIMIZE3`, `OPTIMIZE3`, `float_ops`. Defined functions: `test`, `main`. Referenced calls/builtins: `NEED_GNUC`, `__attribute__`, `optimize`, `float_ops`, `_sin`, `_cos`, `test`.

## Control Flow

Control flow is deliberately linear: helper function(s) `test` initialize data or provide callbacks; one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; conditional compilation or simple runtime branches select the available platform path; `main` invokes `NEED_GNUC`, `__attribute__`, `optimize`, `float_ops`, `_sin`; the program returns `(int)test()` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `math.h`, `../core-version.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_FLOAT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 69 lines.

- Probe category: small compiler/configuration probe.

- Includes: math.h, ../core-version.h.

- Calls/builtins detected: NEED_GNUC, __attribute__, optimize, float_ops, _sin, _cos, test.

- Structs/types detected: none.
