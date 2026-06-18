# File Research: sources/os/linux/linux/fs/xfs/libxfs/xfs_dir2_data.c

## Purpose

Implements shared XFS directory data-block handling for block, leaf, and node directory formats: data entry field access, filetype storage, structural verification, CRC-aware buffer operations, data block initialization, transaction logging ranges, and bestfree/free-space mutation.

## Main Interfaces

- Entry accessors: `xfs_dir2_data_bestfree_p()`, `xfs_dir2_data_entry_tag_p()`, `xfs_dir2_data_get_ftype()`, `xfs_dir2_data_put_ftype()`.
- Verification and buffer ops: `__xfs_dir3_data_check()`, `xfs_dir3_data_buf_ops`, `xfs_dir3_data_header_check()`, `xfs_dir3_data_read()`, `xfs_dir3_data_readahead()`.
- Free-space accounting: `xfs_dir2_data_freefind()`, `xfs_dir2_data_freeinsert()`, `xfs_dir2_data_freescan()`, internal `xfs_dir2_data_freeremove()`.
- Block creation and logging: `xfs_dir3_data_init()`, `xfs_dir2_data_log_entry()`, `xfs_dir2_data_log_header()`, `xfs_dir2_data_log_unused()`.
- Free range mutation: `xfs_dir2_data_make_free()`, `xfs_dir2_data_use_free()`, `xfs_dir3_data_end_offset()`.

## Control Flow And Behavior

Verification walks each active and unused record from the directory data entry offset to the data area end, checking magic values, free-entry tags and back-tags, active entry inode numbers, active entry tags, filetype values, sorted bestfree entries, non-overlapping free ranges, and, for block-format directories, that every active data entry has a matching leaf record and that leaf records are hash sorted with an accurate stale count.

Read verification checks CRCs on v5 filesystems before structural checks; write verification refreshes the LSN, zeros v5 data-header padding, and updates the checksum. Readahead of directory block zero can land on either block-format or data-format storage, so `xfs_dir3_data_reada_verify()` switches buffer ops based on the on-disk magic before verifying.

`xfs_dir3_data_init()` allocates a directory data buffer, initializes v2 or v3 headers, sets the initial bestfree entry to the whole post-header data area, writes a single unused record, logs the header and unused entry, and returns the buffer. Logging helpers record exact byte ranges for data entries, headers, and unused entry head/tail fields.

`xfs_dir2_data_make_free()` merges a newly freed byte range with adjacent unused records when possible, updates or invalidates bestfree entries, and asks callers to rescan when local bestfree updates cannot prove correctness. `xfs_dir2_data_use_free()` carves a range out of an unused record, handling exact, front, back, and middle splits; it validates the source free range and reports corruption through directory sickness marking.

## State And Data Structures

Directory data blocks contain a header, three bestfree records, and a linear sequence of active `xfs_dir2_data_entry` and unused `xfs_dir2_data_unused` records. V5 directory data headers extend the v2 layout with CRC metadata, owner, UUID, block number, LSN, and padding. The bestfree table tracks only the three largest free regions, so some updates require a full data-block rescan.

## Dependencies

Uses directory geometry from `xfs_da_geometry`, transaction buffer logging, DA buffer read/readahead helpers, CRC buffer helpers, directory inode validation and hashing, health marking for directory/attribute forks, and block-directory tail/leaf helpers from the directory format layer.

## Risks And Invariants

- Bestfree entries must stay sorted, non-overlapping, exact when they reference an unused record, and zero-filled after the last valid entry.
- Free-space split/merge logic must keep unused back-tags accurate or later reverse scans can corrupt directory traversal.
- Block-format validation depends on matching data entries to embedded leaf entries by both hash and address.
- The `needscan` protocol is correctness-sensitive because bestfree tracks only three regions.
- CRC metadata checks cannot validate owner fields until `xfs_dir3_data_read()` supplies the expected directory inode.
