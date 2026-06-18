# File Research: sources/os/bsd/netbsd-src/lib/libutil/sockaddr_snprintf.c

## Purpose
Formats socket addresses according to custom percent escapes.

## Key Details
- Supports address families including local, IPv4, IPv6, optional AppleTalk, and optional link-layer.
- Numeric address lookup uses `getnameinfo`.
- Format escapes include numeric address, port, family, length, hostname/service, interface, IPv6 flow/scope, address family name, combined host:port forms, and debug dumps.
- `%?` suppresses `N/A` output for the next unsupported field.
- Returns the would-have-written length like `snprintf`.
- Sets `errno=EAFNOSUPPORT` for unsupported families.

## Dependencies and Role
- Network formatting helper.
