# File Research: sources/os/bsd/freebsd-src/sbin/nvmecontrol/nc_util.c

Purpose: Small utility helpers shared by `nvmecontrol`.

Key behavior:
- `uint128_to_str()` converts an unsigned 128-bit value to decimal text into a caller-supplied buffer and returns the start of the formatted substring.
- `le48dec()` decodes a 48-bit little-endian integer by combining a 32-bit low part and 16-bit high part.

Dependencies:
- `nvmecontrol.h` for `uint128_t`.
- `<sys/endian.h>` for `le16dec()` and `le32dec()`.

Research notes:
- `uint128_to_str()` detects insufficient buffer space by returning `NULL` if the value is not fully consumed.
- `le48dec()` fills a gap not provided by FreeBSD endian helpers.
