# File Research: sources/local-fs/f2fs-tools/fsck/fsck.c

## Purpose
Main consistency checker and repair engine for `fsck.f2fs`. It validates and repairs relationships among NAT, SIT, SSA summaries, checkpoint counters, inode/node/data trees, dentries, xattrs, quota files, orphan inodes, hard links, lost+found reconnection, and zoned-device write pointers.

## Major responsibilities
- Bitmap accounting:
  - Maintains reconstructed main-area usage bitmap.
  - Maintains NAT-derived nid bitmap.
  - Maintains SIT-derived valid-block bitmap.
  - Compares reconstructed state against on-disk metadata during verification.
- Node/NAT/SSA validation:
  - `sanity_check_nat`
  - `sanity_check_nid`
  - `is_valid_ssa_node_blk`
  - `is_valid_ssa_data_blk`
  - Repairs summary entries when `c.fix_on` is enabled and safe.
- Inode tree traversal:
  - `fsck_chk_node_blk`
  - `fsck_chk_inode_blk`
  - `fsck_chk_dnode_blk`
  - `fsck_chk_idnode_blk`
  - `fsck_chk_didnode_blk`
  - Traverses inline data, inline dentries, direct addresses, direct nodes, indirect nodes, and double-indirect nodes.
- Data block validation:
  - `fsck_chk_data_blk` validates block address, summary entry, SIT bitmap, duplicate block usage, and recursively checks directory blocks.
- Directory validation:
  - Checks dentry NIDs, file types, name lengths, hash codes, hash-directory placement, duplicate `.`/`..`, and child inode consistency.
  - Can clear bad dentries and rewrite fixed dentry blocks.
- Inode repair:
  - Fixes invalid `i_links`, `i_blocks`, compression flags/counts, inline-data reserve addresses, inline sizes, casefold flags, extra attribute sizes, xattr tail garbage, extent info, symlink size, inode checksum, and orphan link counts.
- Hard links:
  - Tracks multi-link files through `hard_link_node`.
  - Detects missing/unreachable links.
  - `fix_hard_links` rewrites actual link counts.
- Quotas:
  - Checks quota inodes with `fsck_chk_quota_node`.
  - Compares and rebuilds quota files through `fsck_chk_quota_files`.
- Orphans:
  - `fsck_chk_orphan_node` validates orphan block entries and can remove invalid ones.
- Metadata/global repair:
  - `fsck_chk_meta`
  - `fsck_chk_checkpoint`
  - `fix_nat_entries`
  - `rewrite_sit_area_bitmap`
  - `fix_checkpoint`
  - `fix_checkpoints`
  - `fix_checksum`
- Lost+found:
  - Reconnects valid unreachable non-directory inodes when the lost+found feature is present.
  - Creates or finds `lost+found`, adds links, updates inode name and parent.
- Zoned devices:
  - Checks current segment offsets against write pointers.
  - Can reset or finish zones and realign SIT/write-pointer state.

## Important entry points
- `fsck_init`: allocates fsck bitmaps and dentry traversal state.
- `fsck_chk_meta`: validates metadata counters and NAT/SIT consistency before full verification.
- `fsck_chk_node_blk`: root recursive checker for an inode/node block.
- `fsck_chk_data_blk`: validates and accounts one data block.
- `fsck_chk_orphan_node`: validates checkpoint orphan lists.
- `fsck_chk_quota_node` / `fsck_chk_quota_files`: quota checks and repair.
- `fsck_chk_and_fix_write_pointers`: early zoned-device write-pointer repair.
- `fsck_chk_curseg_info`: validates current segment SIT/SSA types.
- `fsck_verify`: final consistency summary and global repair decision point.
- `fsck_free`: releases allocated fsck state.

## Dependencies
Includes:
- `fsck.h`
- `xattr.h`
- `quotaio.h`
- `<time.h>`

Relies broadly on other fsck modules:
- mount/segment helpers for NAT/SIT/SSA/checkpoint IO
- dir helpers for dentry creation and lost+found linking
- xattr helpers for xattr validation/writeback
- quota helpers for quota accounting/rebuild
- dump helpers for optional lost-file extraction
- zoned-device helpers when compiled with Linux zoned block support

## Repair model
Most repairs are gated by:
- `c.fix_on`
- `f2fs_dev_is_writable()`
- metadata-specific safety checks

The checker often updates in-memory node blocks unconditionally to continue traversal safely, but writes back only when repair mode and writable device state allow it.

## Research notes
This is the highest-risk file in the group. It encodes the cross-metadata invariants of F2FS userspace fsck: every traversal updates reconstructed counters/bitmaps, and final verification compares those against checkpoint/SIT/NAT state before choosing whether to rewrite global metadata.
