# sources/test-tools/stress-ng/test/test-copy-file-range.c

## Purpose

This file is a portable configure probe for `copy_file_range`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `fcntl.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `copy_file_range`.

## Control Flow

Control flow is deliberately linear: `main` invokes `copy_file_range`; the program returns `copy_file_range(0, NULL, 0, NULL, 1024, 0)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `fcntl.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_COPY_FILE_RANGE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 29 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h, fcntl.h.

- Calls/builtins detected: copy_file_range.

- Structs/types detected: none.
