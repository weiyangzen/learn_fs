# File Research: sources/os/linux/linux-stable/fs/befs/btree.h

This header exposes the BeFS B+tree API to the VFS layer.

Exports:
- `befs_btree_find()` for string-key lookup in a B+tree datastream.
- `befs_btree_read()` for ordinal traversal of B+tree keys and values.

Integration:
- `linuxvfs.c` includes this header for directory lookup and readdir.
- The API takes `struct super_block *` and `const befs_data_stream *`, keeping B+tree traversal independent from VFS inode layout.

Risk notes:
- The API is read-only and directory-oriented; it does not expose mutation or non-string key handling.
