# sources/test-tools/stress-ng/test/test-libsctp.c

## Purpose

This file proves that the development header, symbol declarations, and linker inputs for an optional dependency are usable. A successful compile/link feeds `HAVE_LIB_SCTP` and link flags `-lsctp` into the stress-ng configuration, allowing optional stressors or helper paths to be built only when the dependency is present.

## Important APIs, Types, and Functions

Headers: `stdio.h`, `sys/types.h`, `sys/socket.h`, `netinet/sctp.h`. Defined functions: `main`. Referenced calls/builtins: `printf`. Important scalar/library types: `size_t`.

## Control Flow

Control flow is deliberately linear: one or more bounded loops prepare buffers, iterate rows/events, or walk returned lists; conditional compilation or simple runtime branches select the available platform path; `main` invokes `printf`; the program returns `0` so the target expression is consumed and cannot be fully discarded.

## State and Persistence Behavior

the probe may write to standard output when executed, though configuration primarily cares about build success No stress-ng runtime configuration is modified by this file directly.

## Dependencies and Integration Points

Dependencies are header availability for `stdio.h`, `sys/types.h`, `sys/socket.h`, `netinet/sctp.h`; linker availability for `-lsctp`. It integrates through `sources/test-tools/stress-ng/Makefile.config`, whose `check`/`check_header` probes compile these small programs and write generated `configs/HAVE_*` fragments consumed by the main stress-ng build.

## Risks and Portability Notes

Risks: the primary risk is overinterpreting the program exit code; these probes are meant to be small build-time capability checks.

## Test Signals

Test signal: a successful `compile/link` indicates `HAVE_LIB_SCTP`-style support is available; failure should disable only the dependent stress-ng feature rather than fail the entire project build. There are no in-repository unit assertions beyond the compiler, linker, and optional process exit status for this probe.

## Source Facts

- Source length: 47 lines.

- Probe category: external library/header link probe.

- Includes: stdio.h, sys/types.h, sys/socket.h, netinet/sctp.h.

- Calls/builtins detected: printf.

- Structs/types detected: size_t.
