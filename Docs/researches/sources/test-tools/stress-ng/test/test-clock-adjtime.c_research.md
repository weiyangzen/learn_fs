# sources/test-tools/stress-ng/test/test-clock-adjtime.c

## Purpose

This file is a portable configure probe for `memset, clock_adjtime`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `string.h`, `time.h`, `sys/timex.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `memset`, `clock_adjtime`. Important structs/unions/enums: `timex`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `memset`, `clock_adjtime`; the program returns `clock_adjtime(CLOCK_MONOTONIC, &buf)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `string.h`, `time.h`, `sys/timex.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: runtime execution may require privileges or fail with `EPERM`, so the meaningful test signal is usually compile/link success.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CLOCK_ADJTIME capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 40 lines.

- Probe category: type and ABI shape probe.

- Includes: string.h, time.h, sys/timex.h.

- Calls/builtins detected: memset, clock_adjtime.

- Structs/types detected: struct timex.
