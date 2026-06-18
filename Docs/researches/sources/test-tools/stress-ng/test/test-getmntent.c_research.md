# sources/test-tools/stress-ng/test/test-getmntent.c

## Purpose

This file is a portable configure probe for `setmntent, getmntent, printf, endmntent`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `stdio.h`, `mntent.h`. Defined functions: `main`. Referenced calls/builtins: `setmntent`, `getmntent`, `printf`, `endmntent`. Important structs/unions/enums: `mntent`.

## Control Flow

Control flow is deliberately linear: one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; conditional compilation or simple runtime branches select the available platform path; `main` invokes `setmntent`, `getmntent`, `printf`, `endmntent`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may write to standard output when executed, though configuration primarily cares about build success No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdio.h`, `mntent.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETMNTENT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 37 lines.

- Probe category: type and ABI shape probe.

- Includes: stdio.h, mntent.h.

- Calls/builtins detected: setmntent, getmntent, printf, endmntent.

- Structs/types detected: struct mntent.
