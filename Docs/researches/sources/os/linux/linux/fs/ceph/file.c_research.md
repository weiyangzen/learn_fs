# File Research: sources/os/linux/linux/fs/ceph/file.c

## Role

`file.c` implements CephFS regular-file VFS behavior: open/atomic open/create, release, buffered/direct/synchronous/asynchronous I/O, fscrypt-aware reads and writes, cap acquisition around I/O, fallocate hole punching, copy offload, splice read, llseek, and the regular-file operations table.

## Main Interfaces

- `ceph_open()`, `ceph_atomic_open()`, and `ceph_release()` manage VFS file lifetime and MDS open/create requests.
- `ceph_read_iter()`, `ceph_write_iter()`, and `ceph_splice_read()` dispatch user I/O through page cache or OSD requests depending on caps, flags, encryption, and sync mode.
- `__ceph_sync_read()` is exported within the Ceph client for synchronous OSD reads.
- `ceph_fallocate()` supports keep-size hole punching.
- `ceph_copy_file_range()` uses OSD copy-from offload when safe, otherwise falls back to splice copy.
- `ceph_file_fops` wires the regular-file VFS operations.

## Open and File State

`ceph_flags_sys2wire()` maps Linux open flags to MDS wire flags. `prepare_open_request()` creates `OPEN` or `CREATE` requests, chooses auth MDS for write/create/truncate, sets fmode, flags, and create mode.

`ceph_init_file_info()` allocates either `ceph_dir_file_info` or `ceph_file_info`, sets sync mode for `NOPAGECACHE`, gets fmode refs, initializes per-file read/write context tracking, records the filesystem `filp_gen`, and un-inlines data for writable inline-data files. `ceph_init_file()` selects regular, directory, symlink, or special-file behavior.

`ceph_open()`:

- filters VFS-handled create/excl flags,
- prepares fscrypt regular-file access,
- does a client-side MDS auth check when a path alias is available,
- rejects writes to snapped files,
- trivially opens snapdirs,
- reuses existing caps when sufficient,
- otherwise sends an MDS open request and initializes file-private state from returned fmode.

`ceph_renew_caps()` reopens an inode after session loss when current caps cannot satisfy wanted fmode.

## Atomic Open and Async Create

`ceph_atomic_open()` combines lookup/create/open:

- waits on conflicting async unlink,
- strips `O_TRUNC` because VFS permission/truncate happens later,
- checks max-files quota for create,
- allocates a new inode and ACL/security context,
- prepares fscrypt lookup/create metadata,
- sends a parent-locked MDS open/create request,
- handles snapdir lookup and traceless create replies,
- finishes with `finish_no_open()` for splice/negative/symlink cases or `finish_open()` for opened regular files.

Async create is attempted when `ASYNC_DIROPS` is enabled and `try_prep_async_create()` can obtain:

- auth cap and delegated inode number,
- cached valid file layout,
- `CEPH_CAP_FILE_EXCL | CEPH_CAP_DIR_CREATE`,
- complete directory or matching dentry shared generation.

`ceph_finish_async_create()` locally fills a newly delegated inode with synthetic MDS inode data, initializes ACLs, marks `CEPH_I_ASYNC_CREATE`, splices it into the dentry, marks the file created, and opens it before the MDS reply completes. `ceph_async_create_cb()` later reconciles result errors, inode mismatch, mapping errors, shutdown, and cap flushing. `restore_deleg_ino()` returns unused delegated inode numbers on retryable MDS redirects.

## Release

`ceph_release()` frees per-file state, releases fmode refs, drops fscache cookie use for regular files, releases buffered readdir request/name/dir-info for directories, warns on nonempty read/write contexts, and wakes cap waiters.

## Synchronous Reads

`__ceph_sync_read()` bypasses page cache:

- rejects shutdown inodes,
- waits for dirty page cache in range,
- splits reads by OSD object/request limits,
- expands offsets/lengths for fscrypt block alignment,
- uses sparse reads for encrypted files or `SPARSEREAD`,
- allocates page vectors, submits OSD read, updates read/subvolume metrics,
- decrypts sparse extents for encrypted inodes,
- zero-fills short reads that are holes before EOF,
- copies pages to the destination iterator,
- updates `ki_pos` and returns `CHECK_EOF` retry state when needed.

`ceph_read_iter()` acquires read caps and chooses between direct/sync OSD read and `generic_file_read_iter()` depending on cache/lazy caps, `O_DIRECT`, file sync state, and inline data. It retries after fetching size or inline data when EOF/hole/inline handling requires fresh metadata.

## Direct and AIO I/O

`iter_get_bvecs_alloc()` pins iterator pages into a dynamically allocated `bio_vec` array. `put_bvecs()` releases pages and dirties user-backed read pages when needed.

`ceph_direct_read_write()` handles direct reads/writes using OSD requests and can queue asynchronous completion for non-sync kiocbs when the operation is within `i_size` or satisfied by one OSD request. It invalidates page cache on writes, records metrics, zero-fills read holes, updates size on writes, and returns `-EIOCBQUEUED` for queued AIO.

`ceph_aio_complete_req()` handles individual OSD completions, including `-EOLDSNAPC` write retry via workqueue, sparse read finalization, hole zeroing, metrics, bvec release, request release, and aggregate error propagation. `ceph_aio_complete()` completes the user kiocb when all OSD requests finish, updates size and dirty caps for writes, ends DIO, drops cap refs, frees cap flush state, and releases the aggregate request.

## Synchronous Writes and Encryption

`ceph_sync_write()` writes directly to OSDs from user iterators:

- rejects snapped files,
- waits for page cache in range and invalidates fscache,
- aligns encrypted writes to fscrypt block boundaries,
- performs read-modify-write for partial encrypted blocks,
- uses sparse reads and version assertions or exclusive create to avoid overwriting concurrent changes,
- encrypts pages before write,
- submits OSD write requests,
- updates metrics and subvolume metrics,
- retries RMW if object version changed,
- invalidates written page cache ranges,
- updates inode size and caps.

`ceph_write_iter()` is the high-level write path. It allocates a cap flush, starts direct or write I/O serialization, handles append size refresh, generic write checks, max file size, max-bytes quota, OSD/pool full checks, privilege removal, cap acquisition, timestamp/version updates, and then chooses:

- direct or sync OSD write when buffered/lazy caps are unavailable, `O_DIRECT`, sync mode, or prior write error;
- `generic_perform_write()` when buffered writing is allowed.

It handles `-EOLDSNAPC` by dropping locks/caps and retrying with a newer snap context, marks dirty write caps, flushes when quota is approaching, and forces dsync when OSD map/pool is near full.

## Splice Read and Seek

`ceph_splice_read()` mirrors read cap logic for splice. It falls back to `copy_splice_read()` for inline/sync/no-cache-cap cases and uses `filemap_splice_read()` when cache caps are held.

`ceph_llseek()` refreshes size before `SEEK_END`, `SEEK_DATA`, or `SEEK_HOLE`, then delegates to `generic_file_llseek()`.

## Hole Punching

`ceph_fallocate()` supports only `FALLOC_FL_KEEP_SIZE | FALLOC_FL_PUNCH_HOLE` on unencrypted regular head inodes. It locks the inode, clamps punching beyond EOF, acquires write/buffer caps, updates file modification state, invalidates fscache and page cache, zeroes partial cached pages, sends OSD zero/delete/truncate operations across Ceph object layout boundaries via `ceph_zero_objects()`, and marks write caps dirty.

`ceph_zero_partial_object()` selects `ZERO`, `DELETE`, or `TRUNCATE` OSD ops, using the current snap context. `ceph_zero_objects()` respects stripe unit/count/object size to zero complete object sets efficiently.

## Copy Offload

`__ceph_copy_file_range()` tries OSD copy-from2 offload when:

- source/destination are in the same Ceph cluster,
- destination is not snapped,
- `NOCOPYFROM` is not set and copy-from2 has not been disabled,
- layouts are compatible non-striped single-object layouts,
- neither inode is encrypted,
- length is at least one object.

It flushes source and destination ranges, obtains source read and destination write caps with deadlock avoidance, validates source size/destination growth/quota, invalidates destination cache, manually copies initial/final partial objects with splice, and uses `ceph_do_objects_copy()` for full-object remote copies. If OSDs return `-EOPNOTSUPP`, it disables copy offload for the filesystem client. Public `ceph_copy_file_range()` falls back to `splice_copy_file_range()` on unsupported/cross-device cases.

## Metrics and Subvolume Accounting

Read, write, and copy-from paths update `ceph_client_metric` latency/size counters. `ceph_record_subvolume_io()` records nonzero read/write byte counts with start/end latency into the MDS subvolume metric collector; EOF reads are intentionally not counted as I/O.

## Concurrency and State

- Cap refs are acquired before reads/writes to prevent mid-I/O release to MDS.
- `ceph_start_io_read/write/direct()` and matching end calls serialize with truncation, direct I/O, and buffered I/O expectations.
- `i_ceph_lock` protects cap, snap, size, and dirty-cap state.
- Snap contexts are selected from pending cap snaps or `i_head_snapc`.
- Page cache invalidation is used whenever direct/sync writes or hole punching bypass cached data.
- Async create/unlink coordination with `dir.c` relies on dentry flags, delegated inode numbers, directory caps, and MDS callbacks.

## Error Handling

Key errors include `-ESTALE` for shutdown inodes on user I/O, `-EROFS` for writes to snapshots, `-EDQUOT` for quota, `-ENOSPC` for full OSD maps/pools, `-EFBIG` for max size, `-EOPNOTSUPP` for unsupported fallocate/copy-offload cases, and `-EIO` for shutdown or impossible encrypted sparse extent states. `-EBLOCKLISTED` during sync reads marks the filesystem client blocklisted. Write errors set Ceph inode write-error state until a later successful write clears it.

## Operation Table

`ceph_file_fops` exports open/release, llseek, read/write iterators, mmap prepare, fsync, POSIX/flock locking, splice read/write, ioctl/compat ioctl, fallocate, and copy_file_range.
