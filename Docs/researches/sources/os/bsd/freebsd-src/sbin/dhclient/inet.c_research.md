# File Research: sources/os/bsd/freebsd-src/sbin/dhclient/inet.c

## Purpose
Provides portable helpers for dhclient’s internal address representation.

## Main Elements
- `subnet_number()`: bitwise-ANDs address and mask when lengths match.
- `broadcast_addr()`: computes directed broadcast address from subnet and mask.
- `addr_eq()`: compares address lengths and bytes.
- `piaddr()`: renders an IPv4 `iaddr` to a static printable buffer.

## Dependencies And Integration
Used by lease binding, script environment construction, packet source validation, route rejection, and logging.

## Risk Notes
`piaddr()` uses a static buffer and assumes IPv4-sized data when `len != 0`; callers should not retain multiple returned pointers across calls.
