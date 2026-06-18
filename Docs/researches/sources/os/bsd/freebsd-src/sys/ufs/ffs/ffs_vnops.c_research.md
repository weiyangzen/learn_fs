# File Research: sources/os/bsd/freebsd-src/sys/ufs/ffs/ffs_vnops.c

## Role

Implements FFS-specific vnode operations for file I/O, sync, locking, paging, extended attributes, file handles, and paired vnode release. It layers FFS block sizing, allocation, soft updates, snapshots, and UFS2 extended-attribute storage onto the generic UFS vnode operation set.

## Main Responsibilities

- Defines UFS1/UFS2 vnode and FIFO operation vectors.
- Implements `fsync`, `fdatasync`, and vnode-buffer flushing.
- Implements regular file and directory reads.
- Implements regular file and symlink writes.
- Handles direct I/O fallback and clustered I/O.
- Supports UFS2 extended attribute blocks.
- Provides extended attribute VOPs for open/close/get/list/set/delete.
- Integrates with VM page-in through `getpages` and async `getpages`.
- Implements FFS vnode locking with snapshot lock mutation awareness.
- Exports inode/generation file handles.
- Provides `vput_pair` handling for directory compaction and vnode-reclamation races.

## Vnode Operation Vectors

The file registers four operation vectors:

- `ffs_vnodeops1`: UFS1 ordinary vnode ops.
- `ffs_fifoops1`: UFS1 FIFO ops.
- `ffs_vnodeops2`: UFS2 ordinary vnode ops, including extended attributes.
- `ffs_fifoops2`: UFS2 FIFO ops, including extended attributes and `ffsext_strategy()`.

All ordinary vnode vectors inherit from `ufs_vnodeops` and override FFS-specific sync, read, write, reallocblks, locking, page-in, file-handle, and paired release behavior.

## Sync Path

`ffs_fsync()` calls `ffs_syncvnode()` and then, for synchronous soft updates, calls `softdep_fsync()` and retries if dirty buffers reappear.

`ffs_syncvnode()`:

- Flushes softdep inode metadata before full wait syncs.
- Walks dirty vnode buffers.
- Skips or orders indirect blocks based on wait mode, indirect level, and `DATA_ONLY`.
- Calls `softdep_sync_buf()` when dependencies exist.
- Alternates async and sync passes to flush dependency chains.
- Handles truncated-data assertions.
- Waits for outstanding buffer I/O on `MNT_WAIT`.
- Updates inode metadata unless `NO_INO_UPDT` is requested.
- Handles SUJ journal fsync and clears `IN_NEEDSYNC`.

`ffs_fdatasync()` is a data-only `ffs_syncvnode()` call.

## Locking

`ffs_lock()` wraps vnode locking to handle snapshot vnode lock mutation:

- Snapshot vnodes may have `v_vnlock` changed between their private lock and shared `snaplk`.
- If a thread acquires a lock that is no longer the vnode’s current lock, it releases and retries.
- It enables adaptive locking for path lookup cases marked `LK_NODDLKTREAT`.
- Diagnostic builds track exclusive lock generations.

`ffs_unlock_debug()` asserts that modified lazy-list inodes remain on the lazy list and that directory `IN_ENDOFF` state is not leaked at unlock.

## Read Path

`ffs_read()`:

- Supports regular files, directories, and long symlinks.
- Uses `ffs_rawread()` first for `IO_DIRECT` when direct I/O is compiled in.
- Enforces offset and maximum file-size overflow checks.
- Uses unmapped buffer reads and sparse-hole handling.
- Chooses plain `bread`, clustered reads, or readahead depending on mount flags and sequentiality.
- Uses `ffs_read_hole()` to return zeroes for sparse holes reported by `EJUSTRETURN`.
- Moves data with `vn_io_fault_uiomove()` or `vn_io_fault_pgmove()`.
- Sets `IN_ACCESS` unless `noatime` or read-only.

## Write Path

`ffs_write()`:

- Preallocates soft updates journal resources when SUJ is active.
- Supports `IO_APPEND` and enforces append-only files.
- Rejects directory writes.
- Checks file size limits with `vn_rlimit_fsizex()`.
- Uses `UFS_BALLOC()` to allocate or fetch target blocks.
- Uses `BA_CLRBUF` for partial-block writes to prevent stale data exposure.
- Updates vnode pager size before extending writes.
- Updates inode size, `i_size`, and dinode size on extension.
- Uses unmapped buffer uiomove/page move paths.
- Clears invalid full-size buffers after uiomove failures to avoid exposing uninitialized pages through mmap.
- Chooses sync, async, clustered, direct, or delayed writes based on flags and memory pressure.
- Clears setuid/setgid bits after successful non-privileged writes.
- Rolls back writes with `ffs_truncate()` on `IO_UNIT` errors.
- Performs synchronous inode update for `IO_SYNC`.

## Extended Attribute Storage

UFS2 stores extended attributes in inode extension blocks addressed by negative logical block numbers.

Low-level helpers:

- `ffs_extread()` reads from `di_extsize` using negative logical blocks.
- `ffs_extwrite()` writes to extension blocks, grows `di_extsize`, clears buffers as needed, and supports rollback on `IO_UNIT`.
- `ffsext_strategy()` routes negative extension-block I/O correctly for UFS2 and falls back for FIFOs.

In-memory transaction helpers:

- `ffs_findextattr()` searches an aligned packed `struct extattr` area.
- `ffs_rdextattr()` reads and validates the on-disk EA area, truncating at zeroed tails and rejecting overlong entries.
- `ffs_lock_ea()` / `ffs_unlock_ea()` serialize EA transactions through inode flags.
- `ffs_open_ea()` loads the EA area and increments `i_ea_refs`.
- `ffs_close_ea()` commits or aborts, writes the full EA area plus zero padding, frees the cached area on last close, and truncates empty EA storage.

VOPs:

- `ffs_openextattr()` opens an EA transaction.
- `ffs_closeextattr()` optionally commits, rejecting commits on read-only mounts.
- `ffs_deleteextattr()` removes one named attribute and compacts the EA area.
- `ffs_getextattr()` returns one attribute’s size or content.
- `ffs_listextattr()` lists attribute names in a namespace.
- `ffs_setextattr()` appends or rewrites a named attribute, enforces size limits, pads entries to 8-byte alignment, and commits through `ffs_close_ea()`.

## VM Paging

`ffs_getpages()` and `ffs_getpages_async()` choose between the generic vnode pager and buffer-cache pager:

- `ffs_gbp_getblkno()` maps file offsets to FFS logical block numbers.
- `ffs_gbp_getblksz()` reports FFS block size for a logical block.
- `use_buf_pager` sysctl can force buffer pager usage.
- Async getpages invokes the caller’s completion callback when the chosen path does not do so itself.

## File Handles

`ffs_vptofh()` exports inode number and generation in `struct ufid`. This pairs with `ffs_fhtovp()` / `ffs_inotovp()` in `ffs_vfsops.c` for NFS and other file-handle users.

## Paired Vnode Release

`ffs_vput_pair()` is a specialized parent/child release hook used after lookup/create-style operations.

It handles parent directory cleanup before releasing locks:

- If `IN_ENDOFF` is set, truncates the directory to compact unused tail space.
- If `IN_NEEDSYNC` is set, synchronously flushes the directory vnode.
- Releases the directory and optionally the child vnode.

When the child vnode was intentionally left locked by the caller, it handles the possibility that releasing the directory allowed the child to be reclaimed. It may try to reinstantiate the same inode/generation with `ffs_inotovp(..., FFSV_REPLACE_DOOMED)`.

## Research Relevance

This file is the main FFS vnode behavior layer. It is valuable for studying how a production Unix filesystem connects block allocation, buffer cache, VM paging, soft updates, snapshots, extended attributes, and VFS locking into ordinary file read/write and sync semantics.
