# sources/test-tools/stress-ng/test/test-getxattrat.c

## Purpose

This file checks that the local kernel/UAPI headers expose `getxattrat` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `sys/types.h`, `fcntl.h`, `stddef.h`, `linux/xattr.h`. Defined functions: `main`. Referenced calls/builtins: `getxattrat`. Important structs/unions/enums: `xattr_args`. Important scalar/library types: `ssize_t`, `size_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `getxattrat`; the program returns `getxattrat(AT_FDCWD, "/path/to/somewhere", 0, "name", &args, sizeof(args))` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `sys/types.h`, `fcntl.h`, `stddef.h`, `linux/xattr.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches; dummy paths and newer libc wrappers may make execution fail even when declarations exist.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_GETXATTRAT capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 33 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: sys/types.h, fcntl.h, stddef.h, linux/xattr.h.

- Calls/builtins detected: getxattrat.

- Structs/types detected: struct xattr_args, ssize_t, size_t.
