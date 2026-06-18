# File Research: sources/os/linux/linux/fs/jfs/jfs_xtree.h

Public JFS xtree format and API header.

Key responsibilities:
- Defines `xad_t`, the 16-byte extent allocation descriptor containing flags, 40-bit logical offset, length, and physical address.
- Provides construction and extraction macros for XAD offset, address, and length.
- Defines extent flags: new, extended, compressed, not-recorded, and copy-on-write.
- Defines root and page slot limits, entry start index, and `MAXXLEN`.
- Defines `xtheader`, inline inode root `xtroot_t`, and disk xtree page `xtpage_t`.
- Declares xtree operations for lookup, root initialization, insert, extend, update, truncate, pmap truncate, and append.

Important interactions:
- Depends on `jfs_btree.h` and `pxd_t` layout from JFS metadata definitions.
- Shared by extent allocation, file writeback, truncation, symlink storage, resize, and transaction code.

Invariants and risks:
- The on-disk layout is fixed-size and endian-sensitive.
- Logical offsets are split into `off1` and little-endian `off2`; address and length are delegated to `pxd_t`.
- `XTENTRYSTART` reserves header/router slots and must match B-tree code assumptions.
