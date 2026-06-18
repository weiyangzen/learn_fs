# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/convert.c

## Purpose
Provides alignment-safe conversion helpers for DHCP option buffers, which may not be naturally aligned for direct integer access.

## Main Elements
- `getULong()` / `getLong()`: copy 32-bit network-order values out of byte buffers and convert with `ntohl`.
- `getUShort()` / `getShort()`: copy 16-bit network-order values and convert with `ntohs`.
- `putULong()` / `putLong()`: convert 32-bit values with `htonl` and copy into byte buffers.
- `putUShort()` / `putShort()`: convert 16-bit values with `htons` and copy into byte buffers.

## Dependencies And Integration
Includes `dhcpd.h` for integer types and networking declarations. Used by option parsing/formatting and generic parser code to avoid undefined behavior from unaligned casts.

## Risk Notes
The signed variants rely on converting via network-order integer functions and assigning into signed types. The file intentionally uses `memcpy` rather than pointer casts for portability.
