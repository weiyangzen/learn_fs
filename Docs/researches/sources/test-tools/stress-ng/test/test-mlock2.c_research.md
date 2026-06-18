# sources/test-tools/stress-ng/test/test-mlock2.c

## Purpose

This file is a portable configure probe for `mlock2`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `stdint.h`, `sys/mman.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `mlock2`. Important scalar/library types: `uintptr_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `mlock2`; the program returns `mlock2((void *)ptr, 4096, MLOCK_ONFAULT)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `stdint.h`, `sys/mman.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_MLOCK2 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 33 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h, stdint.h, sys/mman.h.

- Calls/builtins detected: mlock2.

- Structs/types detected: uintptr_t.
