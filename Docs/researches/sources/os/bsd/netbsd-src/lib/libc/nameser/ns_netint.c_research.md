# File Research: sources/os/bsd/netbsd-src/lib/libc/nameser/ns_netint.c

Read completely: 65 lines.

This file provides exported 16-bit and 32-bit network-byte-order helpers for resolver code: `ns_get16`, `ns_get32`, `ns_put16`, and `ns_put32`.

The functions are thin wrappers around `NS_GET16`, `NS_GET32`, `NS_PUT16`, and `NS_PUT32` from `<arpa/nameser.h>`, giving callers function symbols in addition to macros.

Security/reliability notes: no internal bounds checks exist; callers must ensure the source or destination buffer has enough bytes.
