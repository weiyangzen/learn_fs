# File Research: sources/os/linux/linux/fs/qnx4/dir.c

## Role

Implements QNX4 directory iteration and directory inode/file operations.

## Key Function

- `qnx4_readdir()`:
  - walks directory file offsets by QNX4 directory entry size;
  - maps directory logical blocks through `qnx4_block_map()`;
  - reads directory blocks with `sb_bread()`;
  - uses `get_entry_fname()` to skip empty/unused entries;
  - computes inode numbers either directly from block/index or from linked directory entries;
  - emits names with `dir_emit()`.

## Operations

- `qnx4_dir_operations`: generic llseek/read, `iterate_shared`, simple fsync, generic setlease.
- `qnx4_dir_inode_operations`: lookup through `qnx4_lookup`.

## Research Notes

QNX4 directories are arrays of 64-byte records where each record can be a real inode entry or a link entry pointing to the actual inode.
