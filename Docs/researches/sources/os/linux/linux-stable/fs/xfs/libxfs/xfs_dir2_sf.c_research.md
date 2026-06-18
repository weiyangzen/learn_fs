# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_dir2_sf.c

## Purpose

`xfs_dir2_sf.c` implements XFS shortform directories, where the directory payload is stored inline in the inode data fork. It handles local-format sizing, lookup/add/remove/replace, conversion to and from block format, verification, and conversion between 4-byte and 8-byte inode-number encodings.

## Shortform Layout Helpers

Shortform entries have variable length:

- Entry fixed fields: `namelen` and data-block offset bytes.
- Name bytes.
- Optional filetype byte if the filesystem has ftype support.
- Inode number stored as either 4 bytes or 8 bytes depending on `hdr->i8count`.

Key helpers:

- `xfs_dir2_sf_entsize` computes one entry's inline size.
- `xfs_dir2_sf_nextentry` advances through variable-length entries.
- `xfs_dir2_sf_get_ino` / `xfs_dir2_sf_put_ino` handle unaligned 4/8-byte entry inode numbers.
- `xfs_dir2_sf_get_parent_ino` / `xfs_dir2_sf_put_parent_ino` handle the inline `..` inode.
- `xfs_dir2_sf_get_ftype` / `xfs_dir2_sf_put_ftype` hide optional filetype layout.

## Conversion with Block Format

`xfs_dir2_block_sfsize` computes whether a block-format directory can fit inline. It iterates active block entries through the block leaf array, skips `.`, stores `..` as the parent inode, counts normal entries, counts large inode numbers, includes optional ftype bytes, and stops early if the computed size exceeds the inode data fork capacity.

`xfs_dir2_block_to_sf` copies a block-format directory into a temporary inline buffer, skipping unused records and `.`, validating `..`, preserving original data offsets for normal entries, then shrinks away the block and installs the local fork data.

`xfs_dir2_sf_addname` converts shortform to block form via `xfs_dir2_sf_to_block` when the new entry cannot fit inline or cannot fit in the eventual block-form offset layout. After conversion it delegates to `xfs_dir2_block_addname`.

## Add, Lookup, Remove, Replace

`xfs_dir2_sf_addname` chooses between:

- Easy append (`xfs_dir2_sf_addname_easy`) when the new record fits after the last represented data offset.
- Hard insert (`xfs_dir2_sf_addname_hard`) when it must use a hole in the represented block layout or convert inode numbers to 8-byte form.

`xfs_dir2_sf_addname_pick` determines whether the new entry fits at all, whether it fits at the end, or whether a hole insertion is needed. It also ensures the equivalent block-format directory would not overflow a directory block.

`xfs_dir2_sf_lookup` special-cases `.` and `..`, then scans entries for exact or case-insensitive matches. Exact matches return `-EEXIST`; misses return `-ENOENT`; CI matches are finalized through `xfs_dir_cilookup_result`.

`xfs_dir2_sf_removename` finds the exact entry, slides later bytes down, shrinks the local data fork, decrements `count`, and updates `i8count`. If the removed entry was the last large inode, it converts the whole shortform directory back to 4-byte inode numbers.

`xfs_dir2_sf_replace` updates `..` or a normal entry's inode/filetype. If replacing with a large inode would exceed local fork capacity, it converts to block form and delegates to `xfs_dir2_block_replace`; otherwise it may convert to 8-byte inode storage in place.

## Verification

`xfs_dir2_sf_verify` checks minimum size, parent inode validity, variable-entry bounds, nonzero names, monotonically increasing data offsets, valid entry inode numbers, valid ftypes, exact end pointer, correct `i8count`, and whether the represented block layout would fit in one directory block. The debug-only `xfs_dir2_sf_check` asserts similar invariants during mutation.

## Inode-Number Width Conversion

`xfs_dir2_sf_toino4` and `xfs_dir2_sf_toino8` rebuild the entire inline directory into a newly sized local fork. They copy fields entry by entry rather than relying on raw layout compatibility because the parent and each entry inode field changes size. `xfs_dir2_sf_toino8` leaves `i8count` set to one before the new large-inode entry is actually installed, matching the caller's flow.

## Dependencies and Interactions

This file is closely coupled with `xfs_dir2_block.c` for shortform/block transitions, with `xfs_dir2_data.c` for block-format entry sizing and ftype conversion, and with `xfs_dir2_priv.h` for shared helper declarations. Scrub and repair code use `xfs_dir2_sf_verify` and shortform field accessors.
