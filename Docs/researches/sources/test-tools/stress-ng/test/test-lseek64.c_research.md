# sources/test-tools/stress-ng/test/test-lseek64.c

## Purpose

This file is a portable configure probe for `open, lseek64, close`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`, `unistd.h`, `fcntl.h`. Local macros: `_LARGEFILE64_SOURCE`. Defined functions: `main`, `if`. Referenced calls/builtins: `open`, `lseek64`, `close`. Important scalar/library types: `off64_t`.

## Control Flow

Control flow is deliberately linear: helper function(s) `if` initialize data or provide callbacks; conditional compilation or simple runtime branches select the available platform path; `main` invokes `open`, `lseek64`, `close`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`, `unistd.h`, `fcntl.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_LSEEK64 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 40 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: sys/types.h, unistd.h, fcntl.h.

- Calls/builtins detected: open, lseek64, close.

- Structs/types detected: off64_t.
