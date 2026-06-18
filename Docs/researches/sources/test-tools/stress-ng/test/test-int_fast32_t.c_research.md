# sources/test-tools/stress-ng/test/test-int_fast32_t.c

## Purpose

This file is a portable configure probe for `uint_fast32_t, int_fast32_t`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `inttypes.h`, `../core-version.h`. Defined functions: `main`. Important scalar/library types: `uint_fast32_t`, `int_fast32_t`.

## Control Flow

Control flow is deliberately linear: `main` declares or sizes the target type and returns a constant or `sizeof` value.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `inttypes.h`, `../core-version.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_INT_FAST32_T capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: type and ABI shape probe.

- Includes: inttypes.h, ../core-version.h.

- Calls/builtins detected: none.

- Structs/types detected: uint_fast32_t, int_fast32_t.
