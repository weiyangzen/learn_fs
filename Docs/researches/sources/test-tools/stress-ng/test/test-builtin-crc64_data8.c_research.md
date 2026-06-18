# sources/test-tools/stress-ng/test/test-builtin-crc64_data8.c

## Purpose

This file is a stress-ng configure test for compiler support of `__builtin_crc64_data8`. It compiles a minimal `main` that invokes the builtin or intrinsic on fixed values so `Makefile.config` can decide whether stress-ng may enable code paths guarded by the corresponding `HAVE_*` capability.

## Important APIs, Types, and Functions

Headers: `stdint.h`. Defined functions: `main`. Referenced calls/builtins: `__builtin_crc64_data8`. Important scalar/library types: `uint64_t`.

## Control Flow

Control flow is deliberately linear: `main` invokes `__builtin_crc64_data8`; the program returns `(int)x` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

there is no persistent repository or filesystem state; local variables, stack buffers, and the process exit status are the only state No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdint.h`; compiler frontend support for the builtin/intrinsic and any target attributes or ISA flags required by that construct. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: builtin names are compiler- and version-specific, so false negatives are expected on otherwise functional platforms.

## Test Signals

Test signal: a successful `compile/link` indicates `a derived HAVE_BUILTIN_CRC64_DATA8 capability`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 27 lines.

- Probe category: compiler builtin and intrinsic probe.

- Includes: stdint.h.

- Calls/builtins detected: __builtin_crc64_data8.

- Structs/types detected: uint64_t.
