# File Research: sources/teaching/xv6-public/stat.h

Defines file types and `struct stat`.

Contents:
- File type constants `T_DIR`, `T_FILE`, and `T_DEV`.
- `struct stat` with type, device, inode number, link count, and byte size.

Shared by kernel and user programs for `stat`/`fstat`.
