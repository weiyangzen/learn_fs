# File Research: sources/os/bsd/freebsd-src/sys/sys/eui64.h

## Purpose
Defines the IEEE EUI-64 address representation and userland conversion routines.

## Main Interfaces
- `EUI64_SIZ`: ASCII representation buffer size.
- `EUI64_LEN`: 8-byte binary length.
- `struct eui64 { u_char octet[8]; }`.
- Userland functions:
  - `eui64_aton`
  - `eui64_ntoa`
  - `eui64_ntohost`
  - `eui64_hostton`

## Dependencies And Integration
The structure is shared ABI for code that handles EUI-64 identifiers. Conversion APIs are not exposed to kernel builds.

## Risk Notes
Binary length and ASCII buffer size are fixed assumptions for callers. Any format change belongs in conversion implementation, not this structure contract.
