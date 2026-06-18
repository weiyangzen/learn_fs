# sources/test-tools/stress-ng/test/test-epoll-create.c

## Purpose

This file is a portable configure probe for `epoll_create`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `sys/epoll.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `epoll_create`.

## Control Flow

Control flow is deliberately linear: `main` invokes `epoll_create`; the program returns `epoll_create(10)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may allocate a kernel object or request kernel data transiently and then returns immediately No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/epoll.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_EPOLL_CREATE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 28 lines.

- Probe category: small compiler/configuration probe.

- Includes: sys/epoll.h.

- Calls/builtins detected: epoll_create.

- Structs/types detected: none.
