# File Research: sources/os/bsd/freebsd-src/sys/sys/stddef.h

## Purpose
`stddef.h` provides minimal FreeBSD standard definitions around null, offsetof, and pointer difference/address types.

## Main Interfaces
- Includes `NULL` and `offsetof` providers.
- Defines `ptraddr_t` when BSD-visible.
- Defines `ptrdiff_t`.

## Implementation Notes
The header avoids redefining typedefs by using `_PTRADDR_T_DECLARED` and `_PTRDIFF_T_DECLARED` guards.

## Dependencies and Constraints
Includes `sys/cdefs.h`, `sys/_null.h`, `sys/_offsetof.h`, `sys/_types.h`, and `sys/_visible.h`.
