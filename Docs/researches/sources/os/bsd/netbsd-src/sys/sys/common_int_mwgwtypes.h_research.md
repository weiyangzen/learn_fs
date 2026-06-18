# File Research: sources/os/bsd/netbsd-src/sys/sys/common_int_mwgwtypes.h

Provides common typedefs for minimum-width, fastest minimum-width, and greatest-width C99 integer types from compiler builtin type macros.

Key content:
- `int_least8_t` through `int_least64_t` and unsigned variants.
- `int_fast8_t` through `int_fast64_t` and unsigned variants.
- `intmax_t` and `uintmax_t`.

Important behavior:
- Requires `__UINT_FAST64_TYPE__`; otherwise emits a preprocessor error.
- Relies entirely on compiler ABI definitions, keeping NetBSD integer typedefs aligned with the target compiler.
