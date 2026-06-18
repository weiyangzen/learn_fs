# File Research: sources/os/bsd/netbsd-src/lib/libwrap/misc.c

## Purpose
Miscellaneous parser/string helpers for `libwrap`.

## Key Details
- `xgets` wraps `fgets`, increments `tcpd_context.line`, and joins backslash-newline continuations.
- `split_at` splits on a delimiter outside square brackets.
- `dot_quad_addr` validates and converts IPv4 dotted-quad strings with `inet_aton`.

## Dependencies and Role
- Used by access table parsing and address matching.
