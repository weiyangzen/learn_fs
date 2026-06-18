# sources/test-tools/stress-ng/test/test-futimens.c

## Purpose

This file is a portable configure probe for `open, unlink, futimens, close`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/time.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`. Defined functions: `main`. Referenced calls/builtins: `open`, `unlink`, `futimens`, `close`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `open`, `unlink`, `futimens`, `close`; the program returns `1` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/time.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_FUTIMENS capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 48 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: sys/time.h, sys/types.h, sys/stat.h, fcntl.h, unistd.h.

- Calls/builtins detected: open, unlink, futimens, close.

- Structs/types detected: none.
