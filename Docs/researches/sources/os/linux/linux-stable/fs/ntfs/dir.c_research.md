# File Research: sources/os/linux/linux-stable/fs/ntfs/dir.c

## Scope

This file implements NTFS directory VFS operations and directory lookup over the `$I30` filename index. It defines the global little-endian `$I30` name, directory lookup by Unicode name, `readdir`/`iterate_shared`, empty-directory checks, directory open/release state, and directory `fsync`.

## APIs And Control Flow

- `I30[5]` is the shared `$I30` Unicode attribute name used by directory and index code.
- `ntfs_lookup_inode_by_name()` maps the directory MFT record, searches the resident `$INDEX_ROOT`, and descends into `$INDEX_ALLOCATION` blocks when needed. It returns an NTFS MFT reference in CPU format or an encoded negative MFT error.
- Lookup first tries case-sensitive equality, then records one permitted case-insensitive match for case-insensitive mounts or DOS namespace aliases. DOS short-name matches allocate a minimal `struct ntfs_name` so `namei.c` can avoid dcache aliasing.
- Index allocation descent reads page-cache folios, copies one page into a temporary buffer, applies MST fixups, verifies `INDX` records, checks VCN and size, and may reuse the same page buffer for child VCNs in the same page.
- `ntfs_filldir()` filters DOS namespace names, root self references, hidden files, and system files according to mount options; converts Unicode names through the mounted NLS table; then emits directory entries with `DT_DIR`, `DT_REG`, or reparse-derived type.
- `ntfs_readdir()` emits `.`/`..`, then iterates the NTFS index through `ntfs_index_ctx_get()`, `ntfs_index_walk_down()`, and `ntfs_index_next()`. It stores the last key in `file->private_data` when userspace stops early so subsequent calls can resume by indexed lookup instead of restarting linearly.
- Readdir batches MFT record readahead ranges in an rb-tree via `struct ntfs_index_ra`, then submits `page_cache_sync_readahead()` on `vol->mft_ino->i_mapping`.
- `ntfs_check_empty_dir()` validates that a directory’s `$INDEX_ROOT` is exactly the empty root size.
- `ntfs_dir_fsync()` flushes parent directory index allocation inodes, this directory’s data range, associated `$BITMAP`, base inode, MFT bitmap, LCN bitmap, `$MFT`, and finally the block device.
- `ntfs_dir_ops` wires directory VFS methods: `llseek`, `read`, `iterate_shared`, `fsync`, `open`, `release`, ioctl, compat ioctl, and leases.

## State And Dependencies

Important state includes `struct ntfs_file_private` resume keys, directory `mrec_lock`, `struct ntfs_index_context`, `$INDEX_ROOT`, `$INDEX_ALLOCATION`, `$BITMAP`, mount flags for hidden/system/case handling, and the NLS/upcase tables.

This file depends on `index.c` for generic B+tree traversal, `mft.c`/attribute search helpers for MFT mapping, `collate` name comparison helpers, reparse tag type lookup, folio/page-cache APIs, rb-trees, and writeback/block flush APIs.

## Risks And Invariants

- Every index entry path is heavily bounds-checked; corruption is reported as directory or index corruption and generally becomes `-EIO`.
- Lookup correctness depends on NTFS collation ordering, not just equality. The code must break and descend at the first key that collates after the requested name.
- The cached case-insensitive match must be unique; a second match is treated as corruption.
- The temporary page copy plus MST fixup avoids inspecting a page while writeback is applying/removing fixups, but it assumes an index block never crosses a page boundary.
- Readdir resume state owns an allocated key buffer and must be released on `release()` or after end-of-iteration.
- Directory fsync reaches outside the current inode into parent indexes and volume metadata; lock nesting and inode references are central to avoiding deadlocks.
