# File Research: sources/os/linux/linux-stable/fs/ntfs3/fslog.c

## Summary
Implements NTFS `$LogFile` restart parsing and crash replay for NTFS3. It defines the on-disk restart/log record structures, validates restart pages and log pages, reconstructs the active log tail, reads client restart data and restart tables, performs analysis/redo/undo passes, applies logged metadata operations to MFT records and index/allocation buffers, rewrites clean restart pages, and tracks when the volume must remain dirty or needs replay.

## Main Responsibilities
- Define NTFS log structures: restart headers/areas, client records, restart tables, open attribute entries, dirty page entries, transaction entries, NTFS restart records, LFS record headers, and record page headers.
- Validate restart page headers, restart areas, client lists, restart tables, log records, MFT records, attributes, index roots, and index buffers before replay mutation.
- Convert between LSNs, file offsets, sequence numbers, and circular-log page offsets.
- Read restart pages and log record pages with USA fixup handling and support for multi-page log records.
- Determine the last valid LSN, including tail-copy and partial-I/O recovery logic.
- Rebuild in-memory open-attribute, dirty-page, attribute-name, and transaction tables from the client restart area and subsequent log records.
- Reopen attributes and reconstruct run mappings needed to replay dirty pages.
- Apply redo operations for dirty pages and undo operations for active uncommitted transactions.
- Mark the volume dirty on replay inconsistency and preserve `NTFS_FLAGS_NEED_REPLAY` when replay cannot complete.

## Key Interfaces
- `log_replay()` is the exported mount-time entry point.
- `check_index_header()` is exported for index validation outside the local replay helpers.
- Local log reading helpers include `read_log_page()`, `log_read_rst()`, `last_log_lsn()`, `read_log_rec_buf()`, `read_rst_area()`, `find_log_rec()`, `read_log_rec_lcb()`, and `read_next_log_rec()`.
- Restart-table helpers include `check_rstbl()`, `enum_rstbl()`, `init_rsttbl()`, `extend_rsttbl()`, `alloc_rsttbl_idx()`, `alloc_rsttbl_from_idx()`, and `free_rsttbl_idx()`.
- `do_action()` is the common redo/undo operation applicator.

## Important Behavior
Replay starts by normalizing the `$LogFile` page size and reading one or two restart pages. If no restart area exists and the log is uninitialized, the code creates an in-memory clean restart area. If a valid restart area exists, it imports page/log sizing, current LSN, sequence-number layout, client records, and open-log count, then calls `last_log_lsn()` to reconcile tail copies and the actual final written log record.

Only NTFS log versions 1.0, 1.1, and 2.0 are accepted. Unsupported versions set the dirty flag and return `-EOPNOTSUPP`. The code also handles legacy restart table formats by converting 32-bit open-attribute and dirty-page entries to the in-memory version-1 form.

The analysis pass begins at the checkpoint LSN, reads forward to the end of the log, updates or creates transaction table entries, updates the dirty page table for records with LCNs, handles `DeleteDirtyClusters` and `HotFix`, tracks open nonresident attributes, and computes the earliest redo LSN from dirty pages and active transactions.

Before redo, the code reopens every logged open attribute. It tries to load the referenced inode and attribute; if it cannot, it creates a synthetic nonresident attribute with an empty runlist so replay can still reason about log records. It then merges dirty-page LCNs into the corresponding run mappings, except for protected early metadata ranges.

The redo pass walks forward from the redo LSN. For each log record that targets a dirty page and is not older than that page's oldest LSN, it verifies the target attribute mapping, trims redo length for deleted clusters, skips no-op/control operations, and calls `do_action()` with the record LSN so MFT/index record LSNs are updated.

The undo pass scans active transactions. It follows each transaction's undo-next chain and applies the logged undo operation through `do_action()` without an LSN pointer, then frees the transaction table entry. Prepared/committed/nonactive transactions are skipped or freed as appropriate.

`do_action()` supports MFT-record operations, resident value changes, nonresident value writes, mapping-pair changes, attribute size updates, root and allocation index entry changes, filename duplicate updates, nonresident bitmap bit set/clear, and record data updates. It validates offsets before every memmove/memcpy, uses `check_lsn()` to avoid replaying stale operations, writes dirty MFT records with `mi_write()`, and writes dirty nonresident buffers back through the reconstructed run mapping.

At successful replay completion, the code updates the MFT mirror, clears `NTFS_FLAGS_NEED_REPLAY`, and writes two clean restart pages with no active client. On read-only mounts, it can analyze enough to leave replay needed without mutating the device; `-EROFS` is converted to success on exit while the replay-needed state remains visible.

## State and Synchronization
`struct ntfs_log` is the central replay context. It holds page sizing, circular-log offsets, LSN sequence fields, restart-area copy, active client id, restart tables, current/oldest/last LSN state, log flags, read-ahead state, and whether replay detected dirty-volume conditions. Replay uses inode lookup/reference ownership, `mi_get()`/`mi_write()` for records not already cached, runlist reconstruction for open attributes, and `ntfs_fix_post_read()`/`ntfs_fix_pre_write()` around multi-sector protected records.

## Cross-File Interactions
Replay uses NTFS3 record schemas from `ntfs.h`/`ntfs_fs.h`, MFT record helpers from `record.c`/`mft.c`, inode loading via `ntfs_iget5()`, attribute lookup and subrecord loading via `frecord.c`, runlist and mapping-pair helpers, bitmap bit helpers, index validation/layout helpers, block-run read/write helpers, and MFT mirror update logic.

## Risks
This file is security- and corruption-sensitive because it replays untrusted on-disk log data into live metadata. Bounds checks on restart tables, attributes, index entries, MFT record `used` sizes, log record offsets, and dirty-page LCN arrays are critical; many later memmove lengths rely on earlier validation. Circular-log tail reconstruction is complex and must distinguish valid tail copies, partial I/O, USA failures, wrapping, and stale pages. Synthetic open attributes allow replay to continue when referenced metadata is damaged, but also make correct dirty-volume marking important. Any replay failure leaves `NTFS_FLAGS_NEED_REPLAY` set and may mark the volume dirty/error.
