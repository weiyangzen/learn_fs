# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/sha3/Makefile.inc

Build fragment for SHA3/Keccak support.

Adds:
- Path `${.CURDIR}/hash/sha3`.
- Sources `keccak.c`, `sha3.c`.

Manpage and MLINK entries are present but commented with `XXX not (yet) public`, indicating the implementation is built but not exposed as public documented API here.
