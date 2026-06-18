# File Research: sources/os/linux/linux/fs/befs/befs_fs_types.h

## Purpose
Defines BeFS on-disk structures and their host-order equivalents. This file is the canonical layout contract for superblocks, inodes, datastreams, block runs, attributes, and B+tree metadata.

## Key Definitions
- Constants:
  - `BEFS_NAME_LEN`, `BEFS_SYMLINK_LEN`, `BEFS_NUM_DIRECT_BLOCKS`, `B_OS_NAME_LENGTH`.
  - `BEFS_DBLINDIR_BRUN_LEN`, fixed at 4, used by double-indirect datastream lookup.
- Superblock flags/magic:
  - `BEFS_SUPER_MAGIC1/2/3`, `BEFS_CLEAN`, `BEFS_DIRTY`.
  - Native byte-order markers and endian-specific constants.
- Inode flags:
  - `BEFS_INODE_IN_USE`, `BEFS_ATTR_INODE`, `BEFS_LONG_SYMLINK`, transaction/write flags.
- Bitwise filesystem-endian scalar types:
  - `fs16`, `fs32`, `fs64`, plus `befs_time_t`.
- Block-run structures:
  - `befs_disk_block_run` uses filesystem-endian fields.
  - `befs_block_run` uses CPU-endian fields.
- Superblock:
  - `befs_super_block` mirrors on-disk layout, including allocation-group geometry, log bounds, root directory, and indices inode.
- Datastream:
  - Direct block-run array, indirect run, double-indirect run, maximum range fields, and byte size.
- Inode:
  - `befs_inode` includes identity, ownership, mode, flags, timestamps, parent/attribute runs, type, inode size, datastream or inline symlink, and small-data area.
- B+tree:
  - `befs_disk_btree_super`, `befs_btree_super`, `befs_btree_nodehead`, and host node header.
  - Key type enum covers string and numeric key classes, though the current driver uses directory string keys.

## Research Notes
All disk structures are `PACKED`, making this file sensitive to unaligned access and endian conversion correctness. It intentionally separates disk-endian and CPU-endian representations for block runs, datastreams, and B+tree state.
