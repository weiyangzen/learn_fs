# File Research: sources/teaching/minix/minix/fs/ext2/super.h

This header defines ext2 superblock and group descriptor structures.

`struct super_block`:
- Starts with the ext2 on-disk superblock fields copied from Linux ext2 definitions.
- Includes dynamic revision fields, feature flags, UUID/name fields, journal-related fields, hash seed/default mount options, and padding.
- Appends in-memory derived state: inode/table sizing, group count, descriptor pointer, block size, sectors per block, max file size, device, read-only flag, allocation search hints, directory counter.

Globals:
- `superblock`: active in-memory superblock.
- `ondisk_superblock`: buffer for disk-format superblock.

`struct group_desc`:
- Tracks block bitmap, inode bitmap, inode table, free block/inode counts, used directories, and reserved fields.

Role:
- Shared metadata model for mount, allocation, inode I/O, statvfs, and sync.
