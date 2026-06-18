# File Research: sources/os/bsd/netbsd-src/lib/libc/net/iso_addr.c

Converters for legacy ISO network addresses. `iso_addr()` parses hexadecimal digits with delimiters into a static `struct iso_addr` containing up to 20 address bytes, using a small state machine for one- and two-nibble bytes.

`iso_ntoa()` converts an ISO address back to dotted lowercase hexadecimal text in a static 64-byte buffer. Both APIs return static storage and are therefore not reentrant.
