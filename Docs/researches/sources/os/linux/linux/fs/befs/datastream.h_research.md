# File Research: sources/os/linux/linux/fs/befs/datastream.h

## Purpose
Public datastream API for BeFS.

## Interfaces
- `befs_read_datastream()`: read a block containing a datastream byte position.
- `befs_fblock2brun()`: map a logical file block to a BeFS block run.
- `befs_read_lsymlink()`: read a long symlink from datastream storage.
- `befs_count_blocks()`: count data and metadata blocks used by a datastream.
- `BAD_IADDR`: shared invalid block-run sentinel.

## Research Notes
This header exposes the block mapping primitives consumed by both `linuxvfs.c` and `btree.c`.
