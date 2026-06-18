# sources/test-tools/stress-ng/test/test-inotify.c

## Purpose

This file is a portable configure probe for `BUFFER_SIZE, inotify_init, inotify_add_watch, read`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `sys/select.h`, `sys/inotify.h`. Local macros: `BUFFER_SIZE`. Defined functions: `main`, `while`. Referenced calls/builtins: `BUFFER_SIZE`, `inotify_init`, `inotify_add_watch`, `read`, `inotify_rm_watch`, `close`. Important structs/unions/enums: `inotify_event`. Important scalar/library types: `ssize_t`.

## Control Flow

Control flow is deliberately linear: helper function(s) `while` initialize data or provide callbacks; one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; conditional compilation or simple runtime branches select the available platform path; `main` invokes `BUFFER_SIZE`, `inotify_init`, `inotify_add_watch`, `read`, `inotify_rm_watch`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present the probe may allocate a kernel object or request kernel data transiently and then returns immediately No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `sys/select.h`, `sys/inotify.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_INOTIFY capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 112 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: unistd.h, sys/select.h, sys/inotify.h.

- Calls/builtins detected: BUFFER_SIZE, inotify_init, inotify_add_watch, read, inotify_rm_watch, close.

- Structs/types detected: struct inotify_event, ssize_t.
