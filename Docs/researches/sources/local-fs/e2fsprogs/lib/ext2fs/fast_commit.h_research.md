# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/fast_commit.h

## Role

Defines ext4 fast-commit on-disk tag constants, TLV structures, replay-state structures for kernel builds, and small helpers shared with the Linux kernel copy.

## Main Contents

- Fast commit tags: add range, delete range, create, link, unlink, inode, pad, tail, head.
- On-disk TLV structures: `ext4_fc_tl`, `ext4_fc_head`, `ext4_fc_add_range`, `ext4_fc_del_range`, `ext4_fc_dentry_info`, `ext4_fc_inode`, `ext4_fc_tail`.
- Reason code enum for fast commit status and ineligibility tracking.
- `__KERNEL__`-only in-memory dentry update, stats, allocation-region, and replay-state structs.
- `tag2str()` maps known tags to diagnostic strings.
- `ext4_fc_tag_len()` returns little-endian TLV length.

## Dependencies

Includes `jfs_compat.h` for fixed-width and endian types. The header states it should remain byte-identical to `linux/fs/ext4/fast_commit.h`.

## Risks / Notes

- The enum intentionally reuses low numeric values by resetting `EXT4_FC_REASON_XATTR = 0` after commit status codes. Consumers must know whether they are interpreting status values or ineligibility counters.
- Flexible array members are expressed as zero-length arrays, matching legacy kernel style.
