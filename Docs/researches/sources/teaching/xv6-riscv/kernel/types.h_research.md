# File Research: sources/teaching/xv6-riscv/kernel/types.h

Defines fixed-width and kernel convenience integer types:
- `uint`, `ushort`, `uchar`.
- `uint8`, `uint16`, `uint32`, `uint64`.
- `pde_t` as `uint64`.

Filesystem relevance: these types are used throughout on-disk structures, block numbers, inode metadata, virtual addresses, and device descriptors.
