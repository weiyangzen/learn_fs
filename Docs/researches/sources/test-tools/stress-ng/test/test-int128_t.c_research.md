# sources/test-tools/stress-ng/test/test-int128_t.c

## Purpose

This file is a portable configure probe for `NEED_GNUC`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `inttypes.h`, `../core-version.h`. Defined functions: `main`. Referenced calls/builtins: `NEED_GNUC`. Important scalar/library types: `__uint128_t`, `__int128_t`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `NEED_GNUC`.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `inttypes.h`, `../core-version.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_INT128_T capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 32 lines.

- Probe category: type and ABI shape probe.

- Includes: inttypes.h, ../core-version.h.

- Calls/builtins detected: NEED_GNUC.

- Structs/types detected: __uint128_t, __int128_t.
