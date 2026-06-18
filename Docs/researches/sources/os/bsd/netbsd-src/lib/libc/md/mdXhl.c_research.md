# File Research: sources/os/bsd/netbsd-src/lib/libc/md/mdXhl.c

Read completely: 109 lines.

This generic template implements high-level digest helpers for an `MDALGORITHM`: `End` finalizes a context and formats the 16-byte digest as lowercase hex, `File` hashes a named file by reading `BUFSIZ` chunks, and `Data` hashes an in-memory buffer.

Important interactions: included by `md4hl.c`, `md5hl.c`, and conditionally `md2hl.c`. Macro concatenation builds algorithm-specific function and context names. Weak aliases are emitted for libc builds.

Security/reliability notes: `End` allocates 33 bytes if caller passes NULL. `File` preserves `errno` across `close`, but if `close` itself fails after successful reads that failure is ignored. Digest size is fixed at 16 bytes, matching MD2/MD4/MD5 only.
