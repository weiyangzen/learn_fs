# sources/test-tools/stress-ng/test/test-execveat.c

## Purpose

This file is a portable configure probe for `syscall`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `fcntl.h`, `sys/syscall.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `syscall`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `syscall`; the program returns `syscall(__NR_execveat, 0, "/proc/self/exe", argv_new, env_new, AT_EMPTY_PATH)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `fcntl.h`, `sys/syscall.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_EXECVEAT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 36 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: unistd.h, fcntl.h, sys/syscall.h.

- Calls/builtins detected: syscall.

- Structs/types detected: none.
