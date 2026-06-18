# File Research: sources/local-fs/e2fsprogs/e2fsck/quota.c

This file handles ext4 quota inode validation and hiding during e2fsck setup.

Main functions:
- `e2fsck_hide_quota(ctx)` moves visible quota files into the hidden quota inode numbers recorded by ext4 when the filesystem has the quota feature and is not read-only.
- `e2fsck_validate_quota_inodes(ctx)` validates quota inode numbers in the superblock and clears invalid references.
- `move_quota_inode(fs, from_ino, to_ino, qtype)` performs the actual inode move.

Move behavior:
- Ensures bitmaps are loaded.
- Reads the visible quota inode.
- Rewrites it as a regular `0600` immutable file at the hidden quota inode number, preserving extents flag when supported.
- Unlinks the old named quota file from root.
- Updates inode allocation stats and clears the original inode on disk.

Validation:
- Rejects quota inode numbers that point to reserved special inodes or exceed `s_inodes_count`.
- Reports `PR_0_INVALID_QUOTA_INO` and clears the superblock field if accepted.

Integration points:
- Uses quota helpers `quota_type2inum()`, `quota_sb_inump()`, and `quota_get_qf_name()`.
- Uses problem codes `PR_0_HIDE_QUOTA` and `PR_0_INVALID_QUOTA_INO`.
- Marks the superblock dirty after modifying quota inode fields.

Risk notes:
- `pctx.dir = 2` in `e2fsck_hide_quota()` is explicitly a best guess for root.
- If move steps fail, the caller continues to the next quota type without updating the superblock field.
