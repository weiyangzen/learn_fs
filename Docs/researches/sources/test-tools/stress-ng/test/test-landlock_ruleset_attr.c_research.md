# sources/test-tools/stress-ng/test/test-landlock_ruleset_attr.c

## Purpose

This file checks that the local kernel/UAPI headers expose `memset` with the expected C shape. It is used by stress-ng configuration to avoid compiling Linux-specific stressors against older, non-Linux, or vendor headers that lack the struct, constant, or syscall wrapper.

## Important APIs, Types, and Functions

Headers: `string.h`, `linux/landlock.h`. Defined functions: `main`. Referenced calls/builtins: `memset`. Important structs/unions/enums: `landlock_ruleset_attr`.

## Control Flow

Control flow is deliberately linear: `main` invokes `memset`; the program returns `sizeof(attr)` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `string.h`, `linux/landlock.h`; Linux-compatible UAPI headers matching the tested kernel feature. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: kernel UAPI structs can vary by header vintage and distribution patches.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_LANDLOCK_RULESET_ATTR capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 31 lines.

- Probe category: Linux kernel UAPI/header or syscall probe.

- Includes: string.h, linux/landlock.h.

- Calls/builtins detected: memset.

- Structs/types detected: struct landlock_ruleset_attr.
