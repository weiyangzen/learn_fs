# File Research: sources/teaching/xv6-riscv/kernel/stat.h

Defines file type constants and user-visible `struct stat`.

Contents:
- `T_DIR`, `T_FILE`, `T_DEVICE`.
- `struct stat` with device, inode number, type, link count, and size.

Filesystem relevance: inode metadata is converted into this structure by `stati()` and exposed to user programs through `fstat`.
