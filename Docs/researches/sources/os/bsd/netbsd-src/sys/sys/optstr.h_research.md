# File Research: sources/os/bsd/netbsd-src/sys/sys/optstr.h

## Purpose
Declares helpers for parsing kernel option strings into strings, numbers, hex/binary numbers, and optionally MAC addresses.

## Main API
- `optstr_get`.
- `optstr_get_string`.
- `optstr_get_number`.
- `optstr_get_number_hex`.
- `optstr_get_number_binary`.
- `optstr_get_macaddr` when Ethernet support is compiled in.

## Dependencies
Includes generated `ether.h`, `sys/types.h`, and `net/if_ether.h` when `NETHER > 0`.

## Risks and Notes
MAC parsing is conditionally compiled on Ethernet support. Callers must pass adequate output buffers and distinguish absent keys from parse failure via the boolean result.
