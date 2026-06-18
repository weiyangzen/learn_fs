# File Research: sources/teaching/xv6-riscv/kernel/param.h

Defines global kernel sizing constants.

Filesystem-relevant constants:
- `NOFILE`, `NFILE`: per-process and global open file limits.
- `NINODE`: active inode cache size.
- `NDEV`: major device table limit.
- `ROOTDEV`: root filesystem disk device.
- `MAXOPBLOCKS`, `LOGBLOCKS`, `NBUF`: transaction, log, and buffer cache sizing.
- `FSSIZE`: filesystem image size in blocks.
- `MAXPATH`: maximum path length.

Filesystem relevance: these constants set the capacity and transaction envelope of xv6’s teaching filesystem.
