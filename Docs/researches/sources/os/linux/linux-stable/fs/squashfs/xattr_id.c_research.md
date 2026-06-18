# File Research: sources/os/linux/linux-stable/fs/squashfs/xattr_id.c

## Summary
Maps Squashfs inode xattr ids to on-disk xattr record locations, sizes, and counts.

## Key APIs
- `squashfs_xattr_lookup()`.
- `squashfs_read_xattr_id_table()`.

## Important Behavior
`squashfs_xattr_lookup()` validates the xattr id, reads the corresponding `squashfs_xattr_id` record from compressed metadata, and returns the xattr table offset, total size, and entry count.

`squashfs_read_xattr_id_table()` reads the xattr id table header, stores the xattr table start and id count, verifies nonzero ids and exact index-table length, reads the index table, checks monotonic compressed-block pointers, and verifies the xattr table precedes the first xattr-id block.

## Risks
The xattr id table sits at the end of the image, so size and ordering checks protect both xattr lookup and the mount-time discovery of earlier tables.
