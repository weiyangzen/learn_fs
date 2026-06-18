# File Research: sources/os/bsd/netbsd-src/lib/libutil/getbyteorder.c

## Purpose
Returns system byte order via sysctl.

## Key Details
- Queries `CTL_HW/HW_BYTEORDER`.
- Returns byte order integer on success.
- Returns `-1` if `sysctl` fails.

## Dependencies and Role
- General hardware metadata helper.
