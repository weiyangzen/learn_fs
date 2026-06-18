# File Research: sources/os/bsd/freebsd-src/sbin/ipf/common/genmask.c

## Purpose
Converts textual IPv4/IPv6 mask specifications into `i6addr_t` mask storage.

## Main Elements
- `genmask()` accepts a protocol family, mask string, and output address union.
- Parses dotted/hex/colon forms as literal IPv4 or IPv6 addresses.
- Parses numeric prefix lengths for IPv4 `/0` through `/32` and IPv6 `/0` through `/128`.
- Uses `inet_aton`, `inet_pton`, `fill6bits`, and network-byte-order IPv4 mask construction.

## Dependencies And Integration
Shared by IPFilter parsing/helpers via `ipf.h`.

## Risk Notes
Family mismatches or malformed masks return `-1`. IPv6 support depends on `USE_INET6`, but the numeric IPv6 case is still present in the switch.
