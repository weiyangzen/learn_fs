# File Research: sources/os/linux/linux-stable/fs/smb/client/file.c

## Summary
Implements the CIFS/SMB client regular-file VFS surface and most open-file lifetime machinery: netfs read/write integration, open/reopen/close, deferred handle close, reconnect recovery, byte-range locking, fsync/flush, strict/loose/direct I/O behavior, mmap setup, oplock/lease break handling, and swap-file operations over SMB.

## Main Responsibilities
- Provide CIFS-specific `netfs_request_ops` callbacks for preparing, issuing, completing, and freeing read/write subrequests.
- Convert Linux open flags into SMB desired access, dispositions, and create options.
- Open files via SMB1 POSIX open when enabled or NT-style SMB open paths otherwise.
- Reuse cached/deferred handles when possible and reopen invalid handles after reconnect.
- Track `struct cifsFileInfo` objects on per-inode and per-tree-connection open lists.
- Flush, close, defer-close, server-close, and release open handles with refcount and workqueue handling.
- Implement mandatory and POSIX byte-range lock test/set/unlock/replay paths.
- Route reads and writes through netfs buffered, unbuffered, strict-cache, loose-cache, and direct-I/O paths.
- Handle oplock/lease breaks by flushing data, invalidating page cache, pushing cached locks, and acknowledging the server.
- Expose address-space operations for netfs page cache, writeback, direct I/O placeholder, migration, invalidation, and experimental SMB3 swap.

## Key Interfaces
- Netfs callbacks: `cifs_prepare_read()`, `cifs_issue_read()`, `cifs_prepare_write()`, `cifs_issue_write()`, `cifs_begin_writeback()`, `cifs_init_request()`, `cifs_free_request()`, `cifs_free_subrequest()`, and `cifs_req_ops`.
- Open lifecycle: `cifs_open()`, `cifs_nt_open()`, `cifs_new_fileinfo()`, `cifs_reopen_file()`, `cifs_close()`, `_cifsFileInfo_put()`, `smb2_deferred_work_close()`, and `serverclose_work()`.
- Reconnect helpers: `cifs_mark_open_files_invalid()`, `cifs_reopen_persistent_handles()`, and `cifs_relock_file()`.
- Handle lookup helpers: `__find_readable_file()`, `__cifs_get_writable_file()`, `find_writable_file()`, `cifs_get_writable_path()`, and `cifs_get_readable_path()`.
- Locking APIs: `cifs_lock()`, `cifs_flock()`, `cifs_getlk()`, `cifs_setlk()`, `cifs_push_locks()`, and legacy POSIX/mandatory lock helpers.
- I/O APIs: `cifs_loose_read_iter()`, `cifs_strict_readv()`, `cifs_file_write_iter()`, `cifs_strict_writev()`, `cifs_writev()`, `cifs_fsync()`, `cifs_strict_fsync()`, and `cifs_flush()`.
- Mapping and cache APIs: `cifs_file_mmap_prepare()`, `cifs_file_strict_mmap_prepare()`, `cifs_oplock_break()`, `is_size_safe_to_change()`, and `cifs_addr_ops`.

## Control Flow And Behavior
Read/write subrequests choose an SMB channel, negotiate missing `rsize`/`wsize`, reserve MTU credits, attach credit debug metadata, optionally configure SMB Direct segment limits, and then submit async SMB read/write calls. Completion releases credits, deregisters SMB Direct memory registrations, updates netfs remote size and zero point for successful writes, and releases xids.

`cifs_open()` builds a dentry-derived server path, handles `O_DIRECT` operation table switching for strict I/O, performs `O_TRUNC` through a server size update, tries to reuse compatible cached readable or writable handles, optionally closes deferred handles for hardlink/path concerns, requests oplocks, opens the file, creates a `cifsFileInfo`, and starts fscache cookie use. Opened files are inserted into both the tree connection open list and the inode open list, with readable handles preferred at the head.

Handle release removes the file from all open lists, cancels or waits for oplock-break work when needed, queues a pending-open entry to avoid missing lease breaks, sends SMB close or close-getattr unless reconnect already invalidated the handle, and offloads final close/free work if server close returns transient busy errors. SMB2 deferred close keeps eligible handles alive for a mount-configured timeout when read/handle caching is active.

Reconnect marks every open handle on a tree connection invalid, invalidates cached directories, and later reopens handles by path or durable/persistent reconnect semantics. Reopen strips create/exclusive/truncate effects, reacquires oplocks, optionally refreshes inode metadata after flushing local dirty data, resets cache if fscache access was downgraded, and replays byte-range locks when a real reconnect occurred.

Strict-cache reads bypass the page cache when no read caching is available or when direct I/O is requested. Strict-cache writes either use cached netfs writes when write caching is allowed or send the exact requested range to the server, invalidating read cache and downgrading oplocks after noncached writes. Loose reads revalidate mappings before using netfs buffered reads. Direct writes invalidate read cache when they could make cached data stale.

Byte-range locking maintains CIFS lock records per open file under `cinode->lock_sem`. If locks can be cached locally, tests and sets may complete without server calls; otherwise the code sends mandatory or legacy POSIX lock requests. Lock conflict checks account for overlapping ranges, shared/exclusive lock type, same fid, process id, OFD locks, and whether the caller is checking a read or write operation.

Oplock breaks wait for pending writers, downgrade local cache flags, break local leases, write back dirty folios, optionally wait and zap the mapping, push cached locks to the server, close deferred handles if handle caching is lost, drop the break reference, and send the protocol-specific oplock response unless the handle was already cancelled or closed.

## State And Synchronization
The file coordinates per-tree `open_file_lock`, per-inode `open_file_lock`, per-file `file_info_lock`, `fh_mutex`, `lock_sem`, deferred-close locks, netfs I/O serialization helpers, inode locks for size updates, delayed/workqueue contexts, and pending-open lists. Correctness depends on not holding the open-list spinlocks across operations that can block and on keeping `cifsFileInfo` references stable while handles are reused, reopened, or asynchronously closed.

## Cross-File Interactions
Protocol behavior is delegated through `server->ops` and `server->vals`, with SMB1/SMB2/SMB3 implementations supplying open, close, async read/write, flush, lock, oplock, fid, and size operations. Mount behavior comes from `fs_context.c` and `fs_context.h` through cache, direct I/O, strict I/O, fscache, multichannel, rsize, and wsize settings. Fscache cookie use and invalidation use `fscache.h`. Directory cached-handle invalidation uses `cached_dir.h`.

## Risks
This file is concurrency-heavy. The highest-risk areas are handle refcount/list lifetime during deferred close and oplock breaks, reconnect reopen ordering, lock replay after reconnect, credit accounting on async I/O failure paths, and cache invalidation when direct or strict writes bypass cached data. Mount options such as `noposixbrl`, strict I/O, fscache, multichannel, SMB Direct, and deferred close materially change behavior, so regressions often appear only under specific server and mount combinations.
