# sources/test-tools/filebench/aslr.h

## Purpose
`aslr.h` is the Filebench header-level dispatch wrapper for ASLR disabling. It exposes one inline `disable_aslr()` API while hiding whether the build uses Linux `personality()` support or a logging-only fallback.

## Important APIs, Types, and Functions
Important declarations are `linux_disable_aslr()`, `other_disable_aslr()`, and `static inline disable_aslr()`. The selection condition matches `aslr.c`: `HAVE_SYS_PERSONALITY_H && HAVE_ADDR_NO_RANDOMIZE`.

## Control Flow and State
Including code calls `disable_aslr()`, which returns the selected void helper. The header has no dynamic control flow beyond compile-time conditional selection.

## Persistence and Dependencies
No state is stored in the header; called implementation may change process personality on Linux. Dependencies: `filebench.h` for shared Filebench declarations/logging context and feature macros supplied by `config.h` transitively in source files.

## Integration Points, Risks, and Test Signals
Integration is any Filebench startup path that needs fixed-address mapping stability. Risks include including `<filebench.h>` with angle brackets, relying on macros being visible before this header, and a void function written with `return helper();`. Test signals are successful compilation on Linux and unsupported platforms and correct call routing to the expected implementation.
