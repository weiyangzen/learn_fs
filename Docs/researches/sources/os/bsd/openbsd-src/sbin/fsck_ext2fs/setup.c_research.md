# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/setup.c

Initializes an ext2 filesystem check: device opening, superblock validation, feature checks, map allocation, and buffer setup.

Setup flow:
- Opens the target via `opendev`, canonicalizes raw device names, validates character-device access, and opens a write fd unless running no-write.
- Reads disklabel sector size when available.
- Pledges down after device setup when not checking hot root.
- Reads the primary superblock, or searches alternates when requested and possible.
- Skips clean filesystems when preening/skip-clean is enabled.
- Computes dynamic ext2 in-memory fields such as block size, group count, group descriptor blocks, inodes per block, and inode-table blocks per group.
- Checks selected superblock invariants, including magic, log block size, blocks per group, reserved block count, blocks/fragments per group agreement, and unsupported feature bits.
- Reads group descriptors.
- Allocates `blockmap`, `statemap`, `typemap`, `lncntp`, and directory inode cache tables.
- Initializes the checker buffer cache.

Supporting routines:
- `readsb` loads and validates superblock state and compares primary vs alternate superblock after normalizing fields allowed to differ.
- `copyback_sb` writes in-memory ext2 superblock fields back to an on-disk buffer.
- `badsb` reports superblock failures.
- `calcsb` builds a prototype ext2 layout from disklabel data to search alternate superblocks.
- `getdisklabel` reads the OpenBSD disklabel.
- `cgoverhead` computes per-block-group metadata overhead, honoring sparse-superblock groups.

This file decides whether an ext2 filesystem is checkable and prepares all global structures for the pass pipeline.
