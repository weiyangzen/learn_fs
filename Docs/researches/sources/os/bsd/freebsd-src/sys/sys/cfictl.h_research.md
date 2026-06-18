# File Research: sources/os/bsd/freebsd-src/sys/sys/cfictl.h

## Purpose
`cfictl.h` defines ioctls for Common Flash Interface query access and Intel StrataFlash protection registers.

## Main Interfaces
- `struct cfiocqry` requests a CFI query read using offset, byte count, and caller buffer pointer.
- `CFIOCQRY` reads CFI query data.
- Protection register ioctls get factory PR, get/set OEM PR, get protection lock register, and set protection lock register.

## Implementation Notes
The interface is small and direct, exposing low-level flash metadata/control operations through ioctl numbers in the `'q'` group.

## Dependencies and Constraints
The header assumes `u_char`, `uint64_t`, `uint32_t`, and ioctl macros are already available from surrounding includes. Protection register operations are hardware-specific.
