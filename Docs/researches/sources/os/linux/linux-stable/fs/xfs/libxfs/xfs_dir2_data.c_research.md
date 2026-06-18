# File Research: sources/os/linux/linux-stable/fs/xfs/libxfs/xfs_dir2_data.c

## Purpose

`xfs_dir2_data.c` implements common manipulation and verification for XFS directory data blocks, shared by block, leaf, and node directory formats. Its core responsibilities are:

- Abstracting v2 versus v3 data headers, especially `bestfree` location and filetype storage.
- Verifying directory data/block buffers, including bestfree ordering, unused-region tags, active entry tags, inode numbers, ftypes, and block-format leaf linkage.
- Reading/readahead of directory data blocks with proper buffer operations, CRC checks, owner checks, and metadata sickness marking.
- Initializing new data blocks and maintaining the top-three free-space table as entries are allocated or freed.

## Main Interfaces

- `xfs_dir2_data_bestfree_p` returns the bestfree table pointer for v2 or v3 data headers.
- `xfs_dir2_data_entry_tag_p`, `xfs_dir2_data_get_ftype`, and `xfs_dir2_data_put_ftype` encapsulate variable on-disk entry layout details.
- `__xfs_dir3_data_check` is the main consistency checker for both data-format and block-format directory blocks.
- `xfs_dir3_data_read` and `xfs_dir3_data_readahead` wrap `xfs_da_read_buf` / `xfs_da_reada_buf` with data-buffer ops and post-verifier owner checks.
- `xfs_dir3_data_init` creates a new data block, writes the correct magic/owner/uuid fields, and initializes the entire usable area as one free entry.
- `xfs_dir2_data_make_free` turns an active byte range into unused space, merging with adjacent free ranges and updating or requesting a rescan of `bestfree`.
- `xfs_dir2_data_use_free` consumes a byte range from an existing unused entry, splitting or trimming it and maintaining `bestfree`.
- `xfs_dir3_data_end_offset` distinguishes the end of data entries in pure data blocks versus block-format directory blocks whose leaf/tail live at the end.

## Verification and Invariants

`__xfs_dir3_data_check` walks the data area from `geo->data_entry_offset` to the format-specific end offset. It enforces:

- The buffer is a data or block directory magic.
- Block-format leaf count is bounded by the remaining block size.
- Bestfree entries are sorted descending by length, zero-length entries have zero offsets, and every listed free extent is seen exactly once.
- Unused entries have the free tag, aligned length, non-overlap, valid trailing tag, and no adjacent free entry left unmerged.
- Active entries have nonzero names, valid record length, valid inode number, valid trailing offset tag, and valid file type.
- For block-format directories, each active data entry has a matching hash/address in the block leaf array, leaf hash order is nondecreasing, and stale counts match.

The verifier separates generic checks (`xfs_dir3_data_verify`) from owner-specific checks (`xfs_dir3_data_header_check`) because owner verification needs the caller's directory inode number.

## Free-Space Update Model

The data-block header tracks only the three largest free regions. `xfs_dir2_data_make_free` and `xfs_dir2_data_use_free` update those slots incrementally when possible and set `needscan` when a full block scan is required to reconstruct correct top-three state. This avoids scanning on common single-region operations while preserving correctness after ambiguous cases, such as splitting an old bestfree entry when the third slot may not be representative.

Important edge cases:

- Freeing a range can merge with the previous entry, next entry, both, or neither.
- Allocating from a free range can consume it exactly, trim the front, trim the back, or split the middle into two unused entries.
- Corruption detected while consuming free space calls `xfs_corruption_error`, marks the directory/attribute operation sick via `xfs_da_mark_sick`, and returns `-EFSCORRUPTED`.

## Dependencies and Callers

This file is a substrate for:

- `xfs_dir2_block.c`, which uses these helpers for block-format add/remove and shortform conversion.
- `xfs_dir2_leaf.c`, which relies on data init/free/use/log helpers for leaf-format data blocks.
- `xfs_dir2_node.c`, which uses the same data-block mechanics while maintaining separate freespace blocks.
- Scrub and repair paths, which reuse layout helpers and bestfree accessors.

## Implementation Notes

The code is careful about logging only modified byte ranges: data entries, unused-entry headers/tags, and data headers have separate log helpers. v3 CRC write verification updates `lsn`, zeroes stale padding, and refreshes the checksum only after structural verification succeeds.
