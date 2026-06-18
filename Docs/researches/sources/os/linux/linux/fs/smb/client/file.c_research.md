# File Research: sources/os/linux/linux/fs/smb/client/file.c

## Role

Implements CIFS/SMB client VFS file operations and address-space behavior: open/close, file handle lifetime, reconnect/reopen, netfs read/write integration, byte-range locking, fsync/flush, mmap preparation, oplock/lease break handling, and experimental swapfile I/O over SMB3.

## Netfs I/O

- `cifs_req_ops` connects the SMB client to the Linux netfs library.
- `cifs_prepare_read()` / `cifs_prepare_write()` pick an SMB channel, negotiate `rsize`/`wsize` when needed, obtain credits through server ops, set subrequest limits, and wire SMB Direct segment limits when RDMA is active.
- `cifs_issue_read()` / `cifs_issue_write()` adjust credits, reopen invalid handles when possible, submit async SMB read/write vectors, and terminate subrequests on failure.
- `cifs_write_subrequest_terminated()` updates netfs remote size and zero-point state after successful direct/unbuffered writes before completing the netfs subrequest.
- Request setup stores the active `cifsFileInfo`, r/w sizes, and optionally forwards the original opener PID for `rwpidforward`.

## Open, Close, And Handle Lifetime

- `cifs_open()` builds the full path, handles direct-I/O file op replacement, performs `O_TRUNC`, tries to reuse deferred cached handles, otherwise performs legacy POSIX open when available or SMB NT-style open through `server->ops->open`.
- `cifs_nt_open()` maps POSIX open flags to SMB desired access/disposition/create options and refreshes inode metadata after open.
- `cifs_new_fileinfo()` allocates and registers `struct cifsFileInfo`, lock lists, work items, tcon/inode open-file lists, and oplock state.
- `cifsFileInfo_put()` / `_cifsFileInfo_put()` manage last-reference close, pending-open protection against missed lease breaks, list removal, server close or close-getattr, retry offload to `serverclose_wq`, and final async freeing.
- `cifs_close()` supports SMB2 deferred close when leases allow handle caching; it records modified attrs, queues delayed close work, or immediately drops the file reference.
- Directory close is separate in `cifs_closedir()`, including search buffer release and protocol-specific directory close handling.

## Reconnect And Reopen

- `cifs_mark_open_files_invalid()` marks all open files on a tcon invalid after reconnect and invalidates cached directories.
- `cifs_reopen_file()` is the central invalid-handle repair path. It rebuilds the path, reopens with legacy POSIX or SMB open, avoids create/truncate flags on reopen, retries access for FS-Cache write-only cases, optionally flushes and refreshes inode metadata, restores oplock state, and relocks server byte-range locks when reconnecting.
- `cifs_reopen_persistent_handles()` walks invalid persistent handles on a tree connection and attempts reopen without flushing.

## Locking

- Mandatory byte-range locks are tracked per file handle in `struct cifs_fid_locks` and per inode under `cinode->lock_sem`.
- `cifs_find_lock_conflict()` and helpers detect overlapping lock conflicts across open FIDs, with special cases for same-FID, same-owner, shared locks, OFD locks, and read/write conflict checks.
- `cifs_lock()` and `cifs_flock()` parse VFS lock requests, choose POSIX vs mandatory SMB locking when legacy UNIX extensions permit, and call `cifs_getlk()` or `cifs_setlk()`.
- `cifs_lock_add_if()` can cache byte-range locks locally when allowed, or block on conflicting local locks using wait queues.
- Legacy paths under `CONFIG_CIFS_ALLOW_INSECURE_LEGACY` push POSIX and mandatory locks back to the server after reconnect and unlock ranges in SMB1 batching format.
- Locking affects cache behavior: setting mandatory locks can zap mappings and downgrade oplocks to avoid stale reads.

## Read/Write, Flush, Fsync, And Mmap

- `cifs_strict_writev()` and `cifs_file_write_iter()` route buffered/direct writes through netfs, serialize writers, honor strict cache policy, flush when write caching is not available, and zap read cache after direct writes.
- `cifs_strict_readv()` chooses buffered or unbuffered netfs reads based on cache rights, direct I/O, strict mode, and byte-range lock conflicts.
- `cifs_loose_read_iter()` revalidates mappings before buffered loose-cache reads.
- `cifs_strict_fsync()` and `cifs_fsync()` write back ranges and issue SMB flushes unless `nostrictsync`/`NOSSYNC` suppresses them.
- `cifs_flush()` writes and checks mapping writeback errors on close.
- `cifs_file_strict_mmap_prepare()` and `cifs_file_mmap_prepare()` revalidate or zap mappings before installing CIFS VM ops with `netfs_page_mkwrite()`.

## Oplocks, Size Safety, And Swap

- `cifs_oplock_break()` waits for pending writers, downgrades oplock/lease state via protocol ops, breaks local leases, writes back data, optionally waits and purges cache, pushes locks, closes deferred handles when handle caching is lost, and sends the protocol oplock response if the file remains open.
- `is_size_safe_to_change()` prevents server metadata refresh from shrinking a locally writable cached inode unless direct I/O or growth makes the update safe.
- `cifs_swap_activate()`, `cifs_swap_deactivate()`, and `cifs_swap_rw()` provide experimental swapfile support using netfs unbuffered I/O and reject sparse swapfiles.
- `cifs_addr_ops` wires netfs folio read/writeback, dirty/release/invalidate/migrate hooks, swap hooks, and `noop_direct_IO`; `cifs_addr_ops_smallbuf` omits readahead for small server buffers.

## Dependencies

Depends on Linux VFS, file locking, writeback, netfs, FS-Cache, SMB Direct, CIFS superblock/inode/session/tcon state, protocol operation tables, path building, tracepoints, and optional legacy CIFS/UNIX extension support.

## Research Notes

This file is the SMB client’s main file-data control plane. Correctness hinges on synchronizing four moving parts: VFS page cache/netfs state, SMB credits and async requests, reopenable server handles, and oplock/lease-driven cache validity. Reconnect and deferred-close paths are especially sensitive because they must avoid missed lease breaks, stale cached data, and lock loss across session failure.
