# sources/test-tools/stress-ng/test/test-fexecve.c

## Purpose

This file is a portable configure probe for `strcmp, open, fexecve`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `fcntl.h`, `string.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `strcmp`, `open`, `fexecve`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `strcmp`, `open`, `fexecve`; the program returns `fexecve(fd, argv_new, env_new)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `fcntl.h`, `string.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_FEXECVE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 36 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: unistd.h, fcntl.h, string.h.

- Calls/builtins detected: strcmp, open, fexecve.

- Structs/types detected: none.
