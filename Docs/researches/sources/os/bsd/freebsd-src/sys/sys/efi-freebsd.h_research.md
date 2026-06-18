# File Research: sources/os/bsd/freebsd-src/sys/sys/efi-freebsd.h

## Purpose
Provides minimal FreeBSD definitions needed by EFI-related code without pulling in the full EDK2 compatibility layer.

## Main Elements
- Header guard and license.
- Includes `sys/_null.h`.

## Dependencies And Integration
Included by `sys/efi.h` to supply minimal FreeBSD-side definitions for EFI type compatibility.

## Risk Notes
Intentionally minimal; consumers needing EDK2 aliases must include the EDK2 adapter rather than assuming this header defines them.
