# sources/test-tools/stress-ng/test/test-fgetxattr.c

## Purpose

This file is a portable configure probe for `fgetxattr`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`. Defined functions: `main`. Referenced calls/builtins: `fgetxattr`. Important scalar/library types: `ssize_t`, `size_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `fgetxattr`; the program returns `fgetxattr(fd, "name", value, sizeof(value))` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_FGETXATTR capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 31 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h.

- Calls/builtins detected: fgetxattr.

- Structs/types detected: ssize_t, size_t.
