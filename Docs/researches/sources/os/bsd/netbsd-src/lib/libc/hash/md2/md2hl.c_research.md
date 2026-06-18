# File Research: sources/os/bsd/netbsd-src/lib/libc/hash/md2/md2hl.c

MD2 instantiation of the generic high-level hash helper.

Defines:
- `HASH_ALGORITHM MD2`
- `HASH_INCLUDE <md2.h>`

Then includes `../hashhl.c`, generating `MD2End`, `MD2FileChunk`, `MD2File`, and `MD2Data`.
