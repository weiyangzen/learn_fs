# File Research: sources/os/bsd/openbsd-src/sbin/dhcpleased/checksum.h

## Purpose
`checksum.h` declares the packet checksum helpers implemented in `checksum.c`.

## Exports
- `checksum(uint8_t *, uint32_t, uint32_t)`
- `wrapsum(uint32_t)`

## Integration Notes
This header assumes callers have included integer type definitions for `uint8_t` and `uint32_t`.
