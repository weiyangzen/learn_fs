# File Research: sources/os/bsd/dragonflybsd/sys/sys/eui64.h

`eui64.h` defines IEEE EUI-64 support. It sets `EUI64_SIZ` for ASCII representation length, `EUI64_LEN` for the eight-byte binary length, and `struct eui64` as an array of eight octets.

For userland it declares conversion helpers: `eui64_aton()`, `eui64_ntoa()`, `eui64_ntohost()`, and `eui64_hostton()`.

This is a small shared ABI/header for link-layer or identifier formatting code.
