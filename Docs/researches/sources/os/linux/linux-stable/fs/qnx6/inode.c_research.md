# File Research: sources/os/linux/linux-stable/fs/qnx6/inode.c

## Summary
Implements QNX6 mount, superblock selection, block mapping, inode loading, statfs, mount options, address-space operations, inode cache, and filesystem registration.

## Main Responsibilities
- Parse the `mmi_fs` mount option.
- Force QNX6 mounts read-only.
- Detect little-endian and big-endian superblocks.
- Validate primary and secondary superblocks with CRC32 and choose the active one by serial number.
- Support the MMI superblock variant through `super_mmi.c`.
- Build private inodes for the inode table and long filename file.
- Map file logical blocks through direct root pointers and indirect pointer trees.
- Load QNX6 inode entries into Linux inodes.
- Register/unregister the `qnx6` filesystem and inode slab cache.

## Key Interfaces
- `qnx6_iget()` loads a filesystem inode.
- `qnx6_block_map()` maps logical blocks to device blocks.
- `qnx6_fill_super()` performs mount validation/setup.
- `qnx6_private_inode()` creates internal metadata inodes.
- `qnx6_statfs()` reports filesystem statistics.
- `qnx6_parse_param()` handles `mmi_fs`.

## Important Behavior
Superblock handling first reads with a 512-byte block size, validates magic and checksum, then switches to the filesystem block size and rereads. A bootblock offset is tried first, then offset zero. The second superblock is located after the data block count plus the superblock area. The active copy is the one with the greater serial number.

Block mapping uses `di_filelevels` to determine indirect depth. The selected direct pointer is based on high bits of the logical block number; each indirect level indexes a block of 32-bit block pointers using `s_ptrbits = ilog2(blocksize / 4)`.

`qnx6_iget()` reads inode entries from the private inode-table inode via page cache, initializes uid/gid/timestamps/size/blocks, copies direct block pointers and file level, and installs read-only file, directory, symlink, or special inode operations.

## State and Synchronization
`struct qnx6_sb_info` stores active superblock buffer, block offset, pointer-bit geometry, mount options, endian mode, and private metadata inodes. `struct qnx6_inode_info` stores block pointers, file levels, and lookup cache.

## Cross-File Interactions
`dir.c` depends on the longfile private inode and endian helpers. `namei.c` calls `qnx6_iget()`. `super_mmi.c` supplies MMI-specific active-superblock selection.

## Risks
The driver is read-only but still follows on-disk pointer trees. It validates superblocks and pointer-level limits, but corrupted indirect pointers can still cause read failures or skipped data.
