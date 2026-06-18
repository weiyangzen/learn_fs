# sources/test-tools/stress-ng/test/test-cap.c

## Purpose

This file is a portable configure probe for `getpid, capget`. It intentionally keeps logic small so the build system can use compile/link success as a feature signal for stress-ng source guarded by generated configuration macros.

## Important APIs, Types, and Functions

Headers: `unistd.h`, `sys/capability.h`. Local macros: `_GNU_SOURCE`. Defined functions: `main`. Referenced calls/builtins: `getpid`, `capget`. Important structs/unions/enums: `__user_cap_data_struct`, `__user_cap_header_struct`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getpid`, `capget`; the program returns `capget(&uch, &ucd)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `unistd.h`, `sys/capability.h`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: runtime execution may require privileges or fail with `EPERM`, so the meaningful test signal is usually compile/link success.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_CAP capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 34 lines.

- Probe category: libc/POSIX feature probe.

- Includes: unistd.h, sys/capability.h.

- Calls/builtins detected: getpid, capget.

- Structs/types detected: struct __user_cap_data_struct, struct __user_cap_header_struct.
