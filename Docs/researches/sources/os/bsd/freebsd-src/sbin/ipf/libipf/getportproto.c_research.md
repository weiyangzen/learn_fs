# File Research: sources/os/bsd/freebsd-src/sbin/ipf/libipf/getportproto.c

This helper resolves a port token for a known numeric protocol.

If the token is all digits, it validates `0..65535` and returns `htons(number)`. Otherwise it maps the numeric protocol to a protocol name through `getprotobynumber()` and calls `getservbyname()`.

It returns the network-byte-order service port or `-1`.
