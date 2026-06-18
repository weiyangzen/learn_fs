# sources/test-tools/stress-ng/test/test-getrandom.c

## Purpose

This file is a portable configure probe for `getrandom`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/random.h`. Defined functions: `main`. Referenced calls/builtins: `getrandom`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getrandom`; the program returns `(int)getrandom(buf, sizeof(buf), 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may allocate a kernel object or request kernel data transiently and then returns immediately No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/random.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_GETRANDOM capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 26 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/random.h.

- Calls/builtins detected: getrandom.

- Structs/types detected: none.
