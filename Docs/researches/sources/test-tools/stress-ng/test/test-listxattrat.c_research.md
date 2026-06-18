# sources/test-tools/stress-ng/test/test-listxattrat.c

## Purpose

This file is a portable configure probe for `listxattrat`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/types.h`, `fcntl.h`. Defined functions: `main`. Referenced calls/builtins: `listxattrat`. Important scalar/library types: `ssize_t`, `size_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `listxattrat`; the program returns `listxattrat(AT_FDCWD, "/some/path/to/somewhere", 0, list, sizeof(list))` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`, `fcntl.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_LISTXATTRAT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 30 lines.

- Probe category: libc/POSIX feature probe.

- Includes: sys/types.h, fcntl.h.

- Calls/builtins detected: listxattrat.

- Structs/types detected: ssize_t, size_t.
