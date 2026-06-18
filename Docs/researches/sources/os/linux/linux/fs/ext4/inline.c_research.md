# File Research: sources/os/linux/linux/fs/ext4/inline.c

## Purpose

`fs/ext4/inline.c` implements ext4 inline data support. Inline data stores small regular-file contents, symlink bodies, and small directory entries inside the inode: first in `ext4_inode.i_block`, then in the in-inode xattr value named `system.data`.

The file owns inline-data sizing, creation, reads/writes, conversion to normal extent/block storage, inline-directory lookup/enumeration/mutation, inline symlink reads, truncate handling, and iomap reporting for inline contents.

## Core Data Model

Important constants:

- `EXT4_XATTR_SYSTEM_DATA`: xattr name `"data"` in the system namespace.
- `EXT4_MIN_INLINE_DATA_SIZE`: size of `i_block`, `sizeof(__le32) * EXT4_N_BLOCKS`, the base inline area.
- `EXT4_INLINE_DOTDOT_OFFSET`: offset of inline directory `..` inode data.
- `EXT4_INLINE_DOTDOT_SIZE`: inline directory stores only the `..` inode number in the first 4 bytes.

Important inode state:

- `EXT4_I(inode)->i_inline_off`: byte offset of the `system.data` xattr entry within the raw inode; zero means no xattr-backed inline payload.
- `EXT4_I(inode)->i_inline_size`: total inline payload capacity, including `i_block`.
- `EXT4_INODE_INLINE_DATA`: persistent inode flag for inline data.
- `EXT4_STATE_MAY_INLINE_DATA`: in-memory state used by write paths to try inline writes before falling back to normal mapping.

The inline payload layout is split:

- bytes `[0, EXT4_MIN_INLINE_DATA_SIZE)` are stored in raw inode `i_block`;
- remaining bytes are stored in the value area of the in-inode xattr `system.data`.

## Main Entry Points

Inline size and discovery:

- `ext4_get_max_inline_size()` computes the maximum inline capacity available in the current inode by inspecting in-inode xattr free space under `xattr_sem`.
- `ext4_find_inline_data_nolock()` locates `system.data`, rejects external xattr-inode references, and initializes `i_inline_off` and `i_inline_size`.
- `get_max_inline_xattr_value_size()` walks the inode xattr table, accounts for entry headers, name length, value offsets, and existing inline xattr value space.

Read/write helpers:

- `ext4_read_inline_data()` copies inline data from `i_block` and optional xattr value into a caller buffer.
- `ext4_write_inline_data()` writes into the same split storage, returning early in ext4 emergency state.
- `ext4_readpage_inline()` and `ext4_read_inline_folio()` fill folio 0 from inline data, zero the tail, and mark the folio uptodate.
- `ext4_read_inline_link()` reads an inline symlink into a newly allocated, terminated buffer.

Inline data creation/update/destruction:

- `ext4_create_inline_data()` creates the `system.data` xattr, zeros `i_block`, clears `EXT4_INODE_EXTENTS`, sets `EXT4_INODE_INLINE_DATA`, and marks the inode dirty.
- `ext4_update_inline_data()` expands the xattr value while preserving existing value contents.
- `ext4_prepare_inline_data()` verifies `EXT4_STATE_MAY_INLINE_DATA`, checks max capacity, locks xattrs, refreshes inline metadata, then creates or updates inline storage.
- `ext4_destroy_inline_data()` wraps `ext4_destroy_inline_data_nolock()` under xattr write locking.
- `ext4_destroy_inline_data_nolock()` removes `system.data`, zeros inline memory, restores extent format when appropriate, clears inline state, and marks the inode dirty.

Conversion to normal storage:

- `ext4_convert_inline_data_to_extent()` converts inline regular-file data during non-delalloc writes. It creates folio 0, reads inline data into it, destroys inline metadata, maps a normal block, journals buffers for data-journal mode, commits the folio, and handles orphan/truncate cleanup on failure.
- `ext4_da_convert_inline_data_to_extent()` handles delayed-allocation conversion by reading inline data into page cache, preparing delayed blocks, marking the folio dirty, and setting `fsdata = CONVERT_INLINE_DATA`.
- `ext4_convert_inline_data_nolock()` converts inline data or inline directories to a real block while holding the xattr lock. It validates inline directory entries before conversion, allocates block 0, initializes directory blocks through `ext4_init_dirblock()`, and restores inline data if conversion fails.
- `ext4_convert_inline_data()` is the exported conversion entry point. If conversion is already in delayed-allocation progress, it flushes the mapping first.

Buffered write integration:

- `ext4_generic_write_inline_data()` starts a small inode transaction, prepares inline storage for `pos + len`, or converts to extent storage if capacity is insufficient. It returns `1` when inline write setup succeeded and returns normal errors otherwise.
- `ext4_try_to_write_inline_data()` rejects writes larger than current maximum inline capacity and otherwise delegates to the generic inline path.
- `ext4_write_inline_data_end()` copies written bytes from the locked folio into inline storage, updates `i_size`, clears folio dirty state so writepages will not process it, stops the journal, and truncates failed over-EOF writes.

Inline directory handling:

- `ext4_try_create_inline_dir()` initializes a new inline directory by storing the parent inode number in the first four inline bytes and creating an empty directory entry over the remaining inline space.
- `ext4_try_add_inline_entry()` first attempts to add a dirent into `i_block` inline space, then xattr inline space, then converts to a real block if no inline room remains.
- `ext4_find_inline_entry()` searches both inline regions for a directory entry.
- `ext4_delete_inline_entry()` deletes an inline dirent using `ext4_generic_delete_entry()`.
- `empty_inline_dir()` validates and scans inline directory entries to determine whether only `.`/`..` remain.
- `ext4_read_inline_dir()` emits inline directory entries to VFS `dir_context`, synthesizing `.` and `..` offsets so directory cookies remain compatible with block-based directories.
- `ext4_inlinedir_to_tree()` feeds inline directory entries into htree readdir state, synthesizing `.` and `..` and hashing entries when needed.
- `ext4_update_inline_dir()` grows the xattr inline directory region when xattr free space permits.
- `ext4_update_final_de()` stretches the last directory entry to cover newly available inline directory space.

Iomap and truncate:

- `ext4_inline_data_iomap()` reports inline data as `IOMAP_INLINE` using the physical address of the raw inode `i_block` area.
- `ext4_inline_data_truncate()` shrinks inline payloads, updates `i_disksize`, truncates xattr value length, zeros the tail in `i_block`, removes stale extent-status entries when needed, and uses orphan handling for crash consistency.

## Dependencies and Integration

This file depends heavily on:

- inode location and raw inode access: `ext4_get_inode_loc()`, `ext4_raw_inode()`;
- xattr internals: `ext4_xattr_ibody_find()`, `ext4_xattr_ibody_set()`, `ext4_xattr_ibody_get()`, xattr header/entry layout helpers;
- journaling: `ext4_journal_start()`, `ext4_journal_get_write_access()`, `ext4_mark_iloc_dirty()`, `ext4_handle_dirty_metadata()`;
- block mapping and writeback: `ext4_block_write_begin()`, `ext4_get_block()`, `ext4_get_block_unwritten()`, `ext4_da_get_block_prep()`;
- directory logic: `ext4_find_dest_de()`, `ext4_insert_dentry()`, `ext4_search_dir()`, `ext4_check_dir_entry()`, `ext4_init_dirblock()`;
- crash consistency: orphan add/delete and failed-write truncation.

## Locking and Ordering

Key locking rules:

- xattr state is protected with `xattr_sem`; many public paths take read or write locks, while `_nolock` helpers require callers to hold the right lock or run during safe initialization.
- inline-data destruction also takes `i_data_sem` write lock because it mutates block mapping state.
- conversion paths coordinate folio locks, xattr locks, journal handles, and orphan-list cleanup.
- inline write end updates `i_size` while holding the folio lock to avoid writeout racing and zeroing past EOF.

## Error Handling and Corruption Checks

The file treats these as corruption or hard failures:

- `system.data` xattr pointing to an external xattr inode returns `-EFSCORRUPTED`.
- missing inline xattr where inline metadata says one should exist returns `-EFSCORRUPTED`.
- inline size larger than `PAGE_SIZE` in folio reads returns `-EFSCORRUPTED`.
- malformed xattr entry walking reports inode errors.
- inline directory conversion validates all dirents before moving them into a real block.
- failed conversion attempts restore inline data when possible; failure to restore logs an emergency data-loss warning.

## Notable Risk Areas

- Inline data shares storage machinery with in-inode xattrs, so xattr compaction and `i_inline_off` changes must be refreshed before writes.
- Conversion paths are crash-sensitive because inline metadata is destroyed before block-backed data is committed; the code uses journaling, orphan handling, and restoration paths to manage this.
- Inline directories have synthetic `.`/`..` layout and offset translation; cookie correctness depends on `i_version` checks and the `extra_offset` calculation in `ext4_read_inline_dir()`.
- `ext4_write_inline_data()` silently returns in emergency state, so callers rely on earlier emergency checks and journal error propagation.
- Inline data and extent flags are mutually exclusive; this file clears and restores flags as storage format changes.
