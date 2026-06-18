# sources/test-tools/stress-ng/test/test-clock-nanosleep.c

## Purpose

This file is a portable configure probe for `clock_nanosleep, clock_settime`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `time.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `clock_nanosleep`, `clock_settime`. Important structs/unions/enums: `timespec`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `clock_nanosleep`, `clock_settime`; the program returns `clock_settime(CLOCK_MONOTONIC, 0, &req, &rem)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `time.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: runtime execution may require privileges or fail with `EPERM`, so the meaningful test signal is usually compile/link success.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CLOCK_NANOSLEEP capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 37 lines.

- Probe category: type and ABI shape probe.

- Includes: time.h.

- Calls/builtins detected: clock_nanosleep, clock_settime.

- Structs/types detected: struct timespec.
