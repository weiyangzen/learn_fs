# File Research: sources/os/bsd/netbsd-src/lib/libresolv/dst_internal.h

Read completely: 166 lines.

Private DST header defining `DST_KEY`, the `dst_func` algorithm dispatch table, key-file constants, secure-free macros, and internal helper prototypes. It establishes fields for key name, size, protocol, algorithm, DNS flags, key id, opaque algorithm-specific key material, and function table.

The header declares the global algorithm table `dst_t_func`, `dst_path`, algorithm initializers, DNS/key-file conversion helpers, network-byte-order helpers, and optional debug dump support. It is the contract between `dst_api.c`, `hmac_link.c`, and `support.c`.
