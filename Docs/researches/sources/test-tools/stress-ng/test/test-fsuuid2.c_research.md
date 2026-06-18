# sources/test-tools/stress-ng/test/test-fsuuid2.c

## Purpose

This file checks that the local kernel/UAPI headers expose `struct fsuuid2` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `linux/fs.h`. Defined functions: `main`. Important structs/unions/enums: `fsuuid2`.

## Control Flow

Control flow is deliberately linear: the program returns `sizeof(uuid)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `linux/fs.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile a declaration/`sizeof` check` indicates `a derived HAVE_FSUUID2 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: linux/fs.h.

- Calls/builtins detected: none.

- Structs/types detected: struct fsuuid2.
