# File Research: sources/os/linux/linux/fs/qnx6/qnx6.h

## Role

Private QNX6 driver header.

## Key Definitions

- Bitwise filesystem integer types `__fs16`, `__fs32`, `__fs64`.
- `struct qnx6_sb_info`: active superblock buffer/pointer, block offset, pointer fanout bits, mount options, endian state, private inode-table inode, and longfile inode.
- `struct qnx6_inode_info`: block pointers, file tree depth, directory lookup hint, and embedded VFS inode.
- Accessors:
  - `QNX6_SB()`
  - `QNX6_I()`

## Endian Helpers

Provides endian-aware conversion helpers:

- `fs64_to_cpu` / `cpu_to_fs64`
- `fs32_to_cpu` / `cpu_to_fs32`
- `fs16_to_cpu` / `cpu_to_fs16`

The selected byte order is stored in `sbi->s_bytesex`.

## API Surface

Declares `qnx6_iget`, `qnx6_lookup`, optional debug superblock printer, directory operations, `qnx6_mmi_fill_super`, and `qnx6_find_ino`.

## Research Notes

Endian abstraction is centralized here, allowing the rest of the QNX6 driver to read normal and big-endian images consistently.
