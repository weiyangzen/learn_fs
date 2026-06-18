# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_sf.c

## Purpose

Implements XFS shortform directories stored inside the inode data fork: variable-length entry encoding, parent and child inode number access, optional filetype storage, block-to-shortform conversion, create/add/lookup/remove/replace operations, shortform verification, and conversion between 4-byte and 8-byte inode-number encodings.

## Main Interfaces

- Entry layout helpers: `xfs_dir2_sf_entsize()`, `xfs_dir2_sf_nextentry()`, `xfs_dir2_sf_get_ino()`, `xfs_dir2_sf_put_ino()`, `xfs_dir2_sf_get_parent_ino()`, `xfs_dir2_sf_put_parent_ino()`, `xfs_dir2_sf_get_ftype()`, `xfs_dir2_sf_put_ftype()`.
- Conversion sizing and conversion: `xfs_dir2_block_sfsize()`, `xfs_dir2_block_to_sf()`.
- Shortform operations: `xfs_dir2_sf_create()`, `xfs_dir2_sf_addname()`, `xfs_dir2_sf_lookup()`, `xfs_dir2_sf_removename()`, `xfs_dir2_sf_replace()`.
- Verification and internal mutation: `xfs_dir2_sf_verify()`, internal `xfs_dir2_sf_addname_easy()`, `xfs_dir2_sf_addname_hard()`, `xfs_dir2_sf_addname_pick()`, `xfs_dir2_sf_toino4()`, `xfs_dir2_sf_toino8()`.

## Control Flow And Behavior

Shortform entries store name length, block-format data offset, name bytes, optional filetype byte, and either 4-byte or 8-byte inode number depending on the header `i8count`. Parent inode storage follows the same width rule. Accessors handle unaligned big-endian loads and stores.

`xfs_dir2_block_sfsize()` computes whether a block-format directory can fit back inside the inode, walking block leaf entries to count non-dot entries, detect `..`, sum names/filetypes, and decide if any inode numbers require 8-byte encoding. `xfs_dir2_block_to_sf()` formats a temporary shortform buffer from the block entries, skips `.`, encodes `..` as the header parent, frees the data block, converts the data fork to local format, copies the shortform data into the inode, updates disk size, and logs core/data fork changes.

`xfs_dir2_sf_addname()` first checks if the new entry still fits in local format and can later be converted to block format. The easy path appends at the end when offset ordering permits. The hard path copies the old directory aside, finds a hole in the block-format offset sequence, rebuilds the inline directory with the new entry inserted, and handles an inode-width conversion first if required. If the shortform directory cannot fit, the code converts to block format and retries through block add.

Lookup special-cases `.` and `..`, then scans entries for exact or first case-insensitive match. Removal slides trailing bytes down, shrinks inline data, updates count and disk size, and may convert from 8-byte inode numbers back to 4-byte if the removed entry was the last large inode number. Replacement handles `..` or a named entry, converts to 8-byte storage when the new inode requires it, can convert to block form if the widened shortform would not fit, and shrinks back to 4-byte encoding if the last large inode number disappears.

`xfs_dir2_sf_verify()` validates minimum size, parent inode, entry bounds, nonzero names, monotonically increasing data offsets, inode numbers, filetype range, exact buffer end, accurate `i8count`, and that the directory still belongs in local format.

## State And Data Structures

The shortform directory is `xfs_dir2_sf_hdr` followed by packed `xfs_dir2_sf_entry` records inside `dp->i_df.if_data`, with `dp->i_df.if_format == XFS_DINODE_FMT_LOCAL` and `dp->i_disk_size == dp->i_df.if_bytes`. Entry offsets preserve the position the entry would occupy in block format, allowing conversion back to block form while maintaining free-space holes.

## Dependencies

Depends on inode local fork resizing, transaction inode logging, block-format conversion helpers, directory comparison/hash utilities, inode data fork size limits, and directory geometry offsets.

## Risks And Invariants

- `i8count` must exactly count parent plus entries requiring 8-byte inode storage.
- Entry offsets must remain monotonically increasing and compatible with later block-format conversion.
- Shortform add/replace must convert to block format before exceeding inline fork size.
- Rebuilding via temporary buffers must preserve filetype bytes and unaligned inode encodings.
- Lookup returns internal `-EEXIST` on success, matching generic directory dispatch expectations.
