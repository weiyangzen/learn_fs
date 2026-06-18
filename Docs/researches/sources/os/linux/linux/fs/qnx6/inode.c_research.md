# File Research: sources/os/linux/linux/fs/qnx6/inode.c

## Role

Main QNX6 filesystem implementation: superblock validation, mount option parsing, block mapping, inode loading, statfs, address-space operations, inode cache, and filesystem registration.

## Mount and Superblock

- Parses `mmi_fs` mount option.
- Always forces read-only mounts.
- Normal QNX6 path:
  - starts with 512-byte superblock reads;
  - tries a bootblock offset first, then offset zero;
  - detects little vs big endian magic;
  - verifies CRC32 checksums for both superblocks;
  - switches block size to on-disk block size;
  - reads the second superblock;
  - chooses the active superblock by serial number.
- MMI path delegates to `qnx6_mmi_fill_super()`.
- Validates inode and longfile tree levels against `QNX6_PTR_MAX_LEVELS`.

## Private Metadata Inodes

- `qnx6_private_inode()` builds internal inodes for the inode table and long filename file from root-node block pointers and tree depth.
- `sbi->inodes` backs inode lookup.
- `sbi->longfile` backs long filename resolution.

## Block Mapping

- `qnx6_block_map()` maps logical file blocks through direct root pointers and optional indirect levels.
- Uses `s_ptrbits = ilog2(blocksize / 4)` to derive pointer fanout.
- Rejects unused block pointers set to all ones.
- `qnx6_get_block()`, `qnx6_read_folio()`, `qnx6_readahead()`, and `qnx6_bmap()` integrate with mpage/generic block helpers.

## Inodes

- `qnx6_iget()` reads inode records from the private inode-table inode, converts endian-aware fields, sets ownership/size/timestamps/block count, stores block pointers/tree depth, and assigns operations for regular files, directories, symlinks, or special inodes.

## Other Operations

- `qnx6_statfs()` reports on-disk block and inode counts.
- `qnx6_checkroot()` verifies that root directory begins with `.` and `..`.
- Registers filesystem type `qnx6` and a slab cache for `qnx6_inode_info`.

## Research Notes

The driver supports endian-flexible QNX6 images and duplicate superblocks. It remains read-only, but its mount path is strict about checksums, tree depth, and root sanity.
