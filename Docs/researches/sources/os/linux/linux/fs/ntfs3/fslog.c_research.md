# File Research: sources/os/linux/linux/fs/ntfs3/fslog.c

## Purpose

Implements NTFS `$LogFile` restart and replay for `ntfs3`. This is the mount-time journal recovery engine: it validates restart pages and log records, reconstructs restart tables, analyzes dirty pages and transactions, performs redo for dirty pages, performs undo for active transactions, updates MFT mirror state, and rewrites clean restart pages.

## Main Structures

- On-disk log/restart structures: `RESTART_HDR`, `RESTART_AREA`, `CLIENT_REC`, `LOG_REC_HDR`, `LFS_RECORD_HDR`, `RECORD_PAGE_HDR`.
- Restart tables: `RESTART_TABLE`, `OPEN_ATTR_ENRTY`, `DIR_PAGE_ENTRY`, `TRANSACTION_ENTRY`, `ATTR_NAME_ENTRY`.
- In-memory replay context: `struct ntfs_log`.
- Per-open-attribute runtime state: `struct OpenAttr`, holding copied attribute metadata and a run tree/reference.

## Main Interfaces

- Public entry point: `log_replay(struct ntfs_inode *ni, bool *initialized)`.
- Shared validator: `check_index_header()`.
- Restart/log helpers: `log_read_rst()`, `last_log_lsn()`, `read_rst_area()`, `read_log_rec_lcb()`, `read_next_log_rec()`.
- Replay mutator: `do_action()`, used by both redo and undo passes.
- Validation helpers: `check_rstbl()`, `check_log_rec()`, `check_file_record()`, `check_attr()`, `check_index_buffer()`, `check_index_root()`.

## Replay Flow

1. Normalize `$LogFile` page/file size and allocate page buffers.
2. Locate restart pages at the primary and secondary restart positions.
3. Select the newest valid restart area, or initialize a fresh log context if the log is uninitialized/CHKDSK-cleaned.
4. Validate supported log versions: 1.0, 1.1, and 2.0.
5. Ensure an `NTFS` client record exists in the restart area.
6. Read the client restart area and reconstruct restart tables:
   - transaction table,
   - dirty page table,
   - attribute name table,
   - open attribute table.
7. Convert legacy version-0 restart records to the current in-memory format where needed.
8. Analysis pass: walk records after the checkpoint, update transaction table state, update dirty page table LCN mappings, process open-attribute records, hotfixes, and transaction state records.
9. Compute the redo LSN from dirty pages and active transactions.
10. If replay is required and the mount is writable, reopen dirty attributes and rebuild/augment their run mappings.
11. Redo pass: walk forward from the redo LSN and apply redo operations for dirty pages whose oldest LSN requires them.
12. Undo pass: for active transactions, follow undo-next chains and apply undo operations.
13. Update MFT mirror, clear `NTFS_FLAGS_NEED_REPLAY`, and write clean restart pages unless read-only.

## `do_action()` Behavior

`do_action()` is the central redo/undo executor. Depending on the log operation, it may:

- Initialize, deallocate, or truncate MFT file record segments.
- Create/delete attributes in file records.
- Update resident values and mapping pairs.
- Set nonresident allocation/data/valid/total sizes.
- Add/delete/update index entries in root or allocation buffers.
- Set index VCNs.
- Update duplicate filename metadata.
- Update arbitrary record data.
- Set/clear bits in nonresident bitmaps.
- Write nonresident value buffers back through run mappings.

Before mutation it loads the target MFT record or target nonresident page, checks LSN ordering, validates file/index/attribute structure, and marks the volume dirty on suspicious corruption.

## Validation and Safety

- Restart-page validation checks signatures, page sizes, versions, restart offsets, USA/fixup layout, client list bounds, sequence-number bits, and restart-area bounds.
- Restart-table validation checks entry sizes, allocated/free-list offsets, free-list integrity, and total counts.
- Log-record validation checks operation target requirements, redo/undo alignment, LCN table consistency, and record length.
- MFT record validation checks file signatures, fixups, record size, used size, in-use status, and every attribute.
- Index validation checks root/allocation headers and entry chains before replaying index operations.
- LSN checks prevent replaying stale operations over newer on-disk records.
- If writable replay is needed but the mount is read-only, `log_replay()` leaves `NTFS_FLAGS_NEED_REPLAY` set and returns success for `-EROFS`.
- Unsupported log versions set dirty/error state and return `-EOPNOTSUPP`.

## Dependencies

- Low-level run I/O: `ntfs_read_run_nb_ra`, `ntfs_read_run_nb`, `ntfs_sb_write_run`.
- Fixup helpers: `ntfs_fix_post_read`, `ntfs_fix_pre_write`.
- MFT helpers: `mi_get`, `mi_write`, `mi_format_new`, `ni_load_mi_ex`, `ntfs_iget5`.
- Run helpers: `run_unpack`, `run_lookup_entry`, `run_add_entry`, `run_close`.
- Bitmap/index helpers: `ntfs_bitmap_set_le`, `ntfs_bitmap_clear_le`, `de_set_vbn_le`.
- Filesystem state: `ntfs_update_mftmirr`, `ntfs_set_state`, `NTFS_FLAGS_NEED_REPLAY`.

## Risk Notes

- This file is intentionally conservative: many malformed structures cause `log->set_dirty = true` rather than trying to continue silently.
- `last_log_lsn()` is complex because it handles wrapped logs, restart tail copies, partial I/O, multi-page records, and log version differences.
- Replay correctness depends on keeping the open attribute table synchronized with attribute mutations; `update_oa_attr()` refreshes copied attributes after relevant changes.
- The redo pass shortens or skips logged writes whose dirty-page LCNs were later deleted.
- The undo pass can expand in-memory attribute sizes so undo operations have addressable target space.
