# sources/test-tools/stress-ng/test/test-finit-module.c

## Purpose

This file checks that the local kernel/UAPI headers expose `finit_module, open` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/module.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`. Defined functions: `main`, `if`. Referenced calls/builtins: `finit_module`, `open`.

## Control Flow

Control flow is deliberately linear: helper function(s) `if` initialize data or provide callbacks; conditional compilation or simple runtime branches select the available platform path; `main` invokes `finit_module`, `open`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

temporary file-descriptor activity may occur against dummy paths, with explicit close/unlink cleanup where present the referenced privileged or kernel-facing call can fail at runtime on normal systems, but compile/link success is the configure signal No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/module.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches; runtime execution may require privileges or fail with `EPERM`, so the meaningful test signal is usually compile/link success; dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link and optionally execute a minimal call path` indicates `a derived HAVE_FINIT_MODULE capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 41 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/module.h, sys/types.h, sys/stat.h, fcntl.h.

- Calls/builtins detected: finit_module, open.

- Structs/types detected: none.
