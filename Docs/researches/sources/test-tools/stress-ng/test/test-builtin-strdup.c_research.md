# sources/test-tools/stress-ng/test/test-builtin-strdup.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_strdup, free`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdlib.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_strdup`, `free`.

## Control Flow

Control flow is deliberately linear: conditional compilation or simple runtime branches select the available platform path; `main` invokes `__builtin_strdup`, `free`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

heap allocation is local to the process and is freed where the probe reaches the cleanup path No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdlib.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_STRDUP capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 31 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdlib.h.

- Calls/builtins detected: __builtin_strdup, free.

- Structs/types detected: none.
