# File Research: sources/os/bsd/netbsd-src/sys/sys/sha2.h

Read completely: 127 lines.

This header declares SHA-224, SHA-256, SHA-384, and SHA-512 constants, context structures, and APIs. `SHA224_CTX` aliases `SHA256_CTX`, and `SHA384_CTX` aliases `SHA512_CTX`.

Each algorithm has `Init`, `Update`, and `Final`; userland also gets `End`, `FileChunk`, `File`, and `Data` helpers. `_LIBC_INTERNAL` exposes transform routines for libc internals.

Risks: context layout is public to callers. Transform prototypes under `_LIBC_INTERNAL` expose lower-level block operations that expect correctly formatted internal state.
