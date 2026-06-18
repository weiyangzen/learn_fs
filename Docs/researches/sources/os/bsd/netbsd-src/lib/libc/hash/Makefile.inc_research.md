# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/Makefile.inc

Top-level libc hash build fragment.

Adds:
- Source `hmac.c`.
- Manpage `hmac.3`.
- Includes subdirectory build fragments for MD2, RMD160, SHA1, SHA2, SHA3, and MurmurHash.

Role: aggregates hash algorithm sources into libc.
