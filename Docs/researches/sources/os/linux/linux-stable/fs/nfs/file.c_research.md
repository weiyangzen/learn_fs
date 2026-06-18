# File Research: sources/os/linux/linux-stable/fs/nfs/file.c

## Role

`file.c` implements regular-file VFS operations for NFS. It dispatches cached and direct reads/writes, handles mmap page-mkwrite, fsync and commit synchronization, page-cache write begin/end, folio invalidation/reclaim laundering, NFS-backed swap activation, and POSIX/flock locking behavior.

## Main interfaces

- `nfs_file_operations`: llseek, read_iter, write_iter, mmap_prepare, open, flush, release, fsync, lock, flock, splice read/write, flag validation, and `FOP_DONTCACHE`.
- `nfs_file_aops`: read folio, readahead, dirtying, writepages, write_begin/write_end, invalidate/release/migrate/launder, dirty/writeback query, error removal, swap activation/deactivation, and swap direct rw.
- `nfs_file_vm_ops`: filemap fault/map_pages plus `nfs_vm_page_mkwrite`.

## Open, close, seek, and flush

`nfs_check_flags()` rejects the unsupported combination of `O_APPEND | O_DIRECT`. `nfs_file_open()` validates flags, calls `nfs_open()`, and marks the file as capable of direct I/O. `nfs_file_release()` clears the NFS open context and releases fscache state.

`nfs_file_llseek()` revalidates file size before `SEEK_END`, `SEEK_DATA`, or `SEEK_HOLE`, then delegates to `generic_file_llseek()`. Size revalidation is forced for `O_DIRECT` or when size cache validity is marked invalid.

`nfs_file_flush()` writes back all dirty pages for writable files and returns writeback errors sampled from the mapping.

## Cached and direct reads

`nfs_file_read()` sends direct reads to `nfs_file_direct_read()` when `IOCB_DIRECT` is set. Cached reads serialize through `nfs_start_io_read()`, revalidate the mapping, call `generic_file_read_iter()`, update normal-read byte stats, and end read serialization.

`nfs_file_splice_read()` follows the same read serialization and mapping revalidation but uses `filemap_splice_read()`.

`nfs_file_mmap_prepare()` first calls `generic_file_mmap_prepare()`, then installs NFS VM ops and revalidates the mapping. Calling generic mmap setup first preserves nommu error behavior.

## Buffered writes

`nfs_file_write()` checks key timeout, dispatches direct writes to `nfs_file_direct_write()`, rejects writes to active swap files, revalidates size for append or writes beyond current `i_size`, clears invalid mapping state, runs generic write checks and `generic_perform_write()` inside NFS write serialization, then applies mount options `WRITE_EAGER` and `WRITE_WAIT`. It calls `generic_write_sync()` and checks mapping writeback errors, forcing full writeback for quota, file-size, or space errors so errors are surfaced reliably.

`nfs_write_begin()` truncates/zeros the last folio for extending writes, gets the target folio, flushes incompatible state, and may perform read-modify-write if the folio is not uptodate, not already private/dirty, not a full overwrite, and pNFS or file-open mode suggests reading first is better.

`nfs_write_end()` zeroes uninitialized regions when extending or partially writing non-uptodate folios, updates NFS folio dirty/private state through `nfs_update_folio()`, unlocks/drops the folio, accounts written bytes, and flushes if the open context key is near expiry.

## Fsync, commits, and folio lifecycle

`nfs_file_fsync()` loops until writeback, NFS COMMIT, pNFS sync, and redirtied-page accounting stabilize. It samples `redirtied_pages` before each iteration to detect writes that became dirty again during commit.

`nfs_truncate_last_folio()` locks the folio containing a truncation/extension boundary, marks it dirty if it had clean PTEs, zeroes the requested segment if uptodate, and emits a tracepoint.

`nfs_invalidate_folio()` writes back or cancels pending NFS writes depending on whether invalidation is partial or whole-folio, waits on deprecated fscache/private_2 state, and traces invalidation. `nfs_release_folio()` refuses reclaim under restricted GFP or kswapd/kcompactd when private state exists, otherwise tries reclaim writeback and fscache release. `nfs_launder_folio()` waits on private_2 state then writes back the folio.

`nfs_check_dirty_writeback()` tells the VM that unstable folios are effectively under writeback while commits are outstanding, or dirty when private state exists and no commit is running.

## mmap write faults

`nfs_vm_page_mkwrite()` handles shared writable mappings. It starts a pagefault write section, waits for fscache/private storage and NFS invalidation to finish, locks and validates the folio still belongs to the inode mapping, waits for writeback, rejects zero-length folios, flushes incompatible state, and calls `nfs_update_folio()` for the full valid folio length. Failures map to retry or SIGBUS-style VM faults.

## Swap support

`nfs_swap_activate()` verifies the swapfile has no holes by comparing `i_blocks` against `i_size`, activates RPC swap behavior, adds one full-file swap extent, enables protocol-specific swap hooks if present, and sets `SWP_FS_OPS`. Deactivation reverses RPC/protocol swap state.

## File locking

`nfs_lock()` handles POSIX locks. It rejects reclaim, honors local lock mount options, validates protocol lock bounds, and dispatches to getlk, unlock, or setlk helpers. `do_setlk()` flushes mapping data before server locks, then treats successful locking as a cache-coherency point by syncing and invalidating caches unless a delegation is held. `do_unlk()` writes back all data and waits for outstanding lock-context I/O before unlocking, with special handling for process-exit `FL_CLOSE`.

`nfs_flock()` simulates flock locks via POSIX locks on the server unless local flock mode is configured.
