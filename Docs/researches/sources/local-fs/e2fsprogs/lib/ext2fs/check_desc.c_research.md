# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/check_desc.c

Implements `ext2fs_check_desc`, a sanity check for ext2/ext4 group descriptors. It verifies descriptor size, metadata block placement, and collisions among superblock/GDT reservations, block bitmaps, inode bitmaps, and inode tables.

Algorithm:
- Verify descriptor size is a power of two.
- Allocate a subcluster bitmap named `check_desc map`.
- Reserve superblock and group descriptor blocks for every group.
- For each group, choose allowed block range. Without `flex_bg`, the range is the group’s own first/last block; with `flex_bg`, the broader filesystem data range is allowed.
- Check block bitmap location is in range and not already reserved/used.
- Check inode bitmap location similarly.
- Check inode table range fits and does not collide with existing marks.
- Mark each accepted structure block in the temporary bitmap.

Returns specific descriptor errors such as bad block map, bad inode map, or bad inode table.

Dependencies: block bitmap allocation, descriptor accessors from `blknum.c`, super/GDT reservation helpers.

Implementation notes:
- The function frees the temporary bitmap on all exit paths.
- It relies on bitmap collision detection to catch overlapping metadata structures.
