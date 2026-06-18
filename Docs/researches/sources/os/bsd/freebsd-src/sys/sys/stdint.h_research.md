# File Research: sources/os/bsd/freebsd-src/sys/sys/stdint.h

## Purpose
`stdint.h` defines FreeBSD's standard integer least/fast typedefs and related portability macros.

## Main Interfaces
- Imports machine and generic fixed-width integer definitions.
- Defines `int_least*`, `uint_least*`, `int_fast*`, and `uint_fast*` typedefs.
- Defines GNU/Darwin-compatible `__WORDSIZE`.
- Defines `WCHAR_MIN`, `WCHAR_MAX`, optional C11 Annex K `RSIZE_MAX`, and C23 integer width macros.

## Implementation Notes
The width macros are exposed only when `__ISO_C_VISIBLE >= 2023`. `RSIZE_MAX` is exposed under `__EXT1_VISIBLE`.

## Dependencies and Constraints
Includes `sys/cdefs.h`, `sys/_types.h`, `machine/_stdint.h`, and `sys/_stdint.h`.
