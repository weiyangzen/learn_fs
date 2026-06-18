# sources/test-tools/stress-ng/test/test-fanotify.c

## Purpose

This file is a portable configure probe for `BUFFER_SIZE, posix_memalign, fanotify_init, free`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `fcntl.h`, `unistd.h`, `stdlib.h`, `mntent.h`, `sys/select.h`, `sys/fanotify.h`. Local macros: `BUFFER_SIZE`. Defined functions: `main`, `if`, `FAN_EVENT_OK`. Referenced calls/builtins: `BUFFER_SIZE`, `posix_memalign`, `fanotify_init`, `free`, `fanotify_mark`, `read`, `FAN_EVENT_OK`, `FAN_EVENT_NEXT`, `close`. Important structs/unions/enums: `fanotify_event_metadata`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: helper function(s) `if`, `FAN_EVENT_OK` initialize data or provide callbacks; one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; conditional compilation or simple runtime branches select the available platform path; `main` invokes `BUFFER_SIZE`, `posix_memalign`, `fanotify_init`, `free`, `fanotify_mark`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal heap allocation is local to the process and is freed where the probe reaches the cleanup path No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `fcntl.h`, `unistd.h`, `stdlib.h`, `mntent.h`, `sys/select.h`, `sys/fanotify.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_FANOTIFY capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 106 lines.

- Probe category: POSIX/Linux runtime API probe.

- Includes: fcntl.h, unistd.h, stdlib.h, mntent.h, sys/select.h, sys/fanotify.h.

- Calls/builtins detected: BUFFER_SIZE, posix_memalign, fanotify_init, free, fanotify_mark, read, FAN_EVENT_OK, FAN_EVENT_NEXT, close.

- Structs/types detected: struct fanotify_event_metadata, size_t.
