# File Research: sources/os/bsd/netbsd-src/sys/sys/common_int_types.h

Defines NetBSD internal exact-width integer typedefs and pointer-sized integer typedefs from compiler builtin type macros.

Key content:
- Internal exact-width types: `__int8_t`, `__uint8_t`, through `__int64_t`, `__uint64_t`.
- Defines `__BIT_TYPES_DEFINED__`.
- Pointer integer types: `__intptr_t`, `__uintptr_t`.

Important behavior:
- Requires `__UINTPTR_TYPE__`; otherwise emits a preprocessor error.
- This header is a low-level ABI bridge used by public type headers.
