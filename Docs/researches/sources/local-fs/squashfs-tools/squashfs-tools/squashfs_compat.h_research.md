# File Research: sources/local-fs/squashfs-tools/squashfs-tools/squashfs_compat.h

This header defines compatibility on-disk layouts for Squashfs 1.x, 2.x, and 3.x filesystems. It is consumed by the legacy `unsquash-*` readers to parse old superblocks, inode formats, directory entries, fragment entries, and bitfield-packed structures.

Key contents:
- 3.x layout: `squashfs_super_block_3`, v3 inode headers, directory index/header/entry types, fragment entry, and swap macros.
- 1.x layout: compact inode headers with 4-bit uid/gid indexes and no fragment table support.
- 2.x layout: v2 inode and directory formats, fragment entries, and packed directory index fields.
- Compatibility constants such as `SQUASHFS_UIDS`, `SQUASHFS_GUIDS`, `SQUASHFS_TYPES`, and old `SQUASHFS_CHECK_DATA`.
- Bitfield-aware `SQUASHFS_SWAP_*_{1,2,3}` macros for cross-endian legacy metadata.

Important behavior:
- The swap macros reconstruct bitfields by copying raw bytes into a 64-bit scratch value and shifting according to host byte order.
- `SQUASHFS_MEMSET(s, d, n)` zeroes the destination structure before assigning swapped fields, which avoids stale padding or unused fields.
- v2 and v3 use different fragment index widths: v2 indexes are 32-bit, v3 indexes are 64-bit.

Corruption-sensitive details:
- Legacy readers depend on exact bit positions in these macros; changing structure fields or swap offsets breaks old-image compatibility.
- The header assumes `SQUASHFS_METADATA_SIZE` and core v4 types from `squashfs_fs.h` are already available.
