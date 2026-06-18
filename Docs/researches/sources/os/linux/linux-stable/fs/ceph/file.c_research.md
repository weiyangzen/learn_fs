# File Research: sources/os/linux/linux-stable/fs/ceph/file.c

## Purpose

`file.c` implements CephFS regular-file open, close, read, write, direct I/O, async direct I/O completion, atomic open/create, fallocate hole punching, llseek, splice read, and copy_file_range offload. It is the main bridge between Linux file operations, Ceph capabilities, page cache policy, fscrypt constraints, FS-Cache invalidation, MDS metadata operations, and OSD object I/O.

## Main Responsibilities

- Defines `ceph_file_fops`.
- Converts Linux open flags to Ceph MDS wire flags.
- Initializes and releases per-file and per-directory private state.
- Opens files locally when existing caps are sufficient or through MDS `OPEN`/`CREATE` requests otherwise.
- Supports async create using delegated inode numbers and directory create caps.
- Implements atomic open with lookup/create/open in one MDS request.
- Implements synchronous OSD reads and writes.
- Implements direct read/write with bvec-backed OSD requests and optional AIO completion.
- Routes buffered reads/writes through generic VFS helpers when cache/buffer caps permit.
- Handles inline-data reads by forcing getattr of inline data.
- Records global and subvolume I/O metrics.
- Performs hole punching with object zero/delete/truncate operations.
- Offloads eligible `copy_file_range()` calls to OSD copy-from operations.
- Integrates cap dirtying, cap flush preallocation, quota checks, and writeback sync behavior.

## Open and File State

`prepare_open_request()` creates MDS `OPEN` or `CREATE` requests and chooses auth MDS when flags imply writing, creation, or truncation.

`ceph_init_file_info()`:
- Allocates `ceph_file_info` or `ceph_dir_file_info`.
- Initializes fmode refs with `ceph_get_fmode()`.
- Sets synchronous I/O mode for `NOPAGECACHE`.
- Initializes per-file rw context tracking.
- Uninlines data before opening inline regular files for write.

`ceph_open()`:
- Validates fscrypt opens for regular files.
- Rejects write opens on snapshots.
- Opens snapdir locally.
- Uses existing caps locally when possible, touching wanted file mode and optionally checking caps asynchronously.
- Otherwise sends an MDS open request and initializes file state from the returned fmode.
- Performs an MDS-side access check when a path alias is available, returning local `-EACCES` only for definite denial.

`ceph_release()` drops fmode refs, FS-Cache cookie use, pending readdir request references, dirstat buffers, and private file caches, then wakes cap waiters.

## Atomic Open and Async Create

`ceph_atomic_open()` combines lookup/create/open behavior:
- Strips `O_TRUNC`; VFS handles truncation after permission checks.
- Waits for conflicting async unlink.
- Performs local MDS access check when possible.
- Allocates a new inode and ACL/security context for create.
- Prepares encrypted lookup/create state when the parent is encrypted.
- Sends MDS `OPEN`/`CREATE`, handles snapdir lookup, traceless create replies, spliced dentries, symlinks, and no-open retry paths.

Async create is attempted when `ASYNC_DIROPS` is enabled and prerequisites hold:
- Parent has auth cap and `FILE_EXCL | DIR_CREATE`.
- Parent has a valid cached file layout.
- Session has delegated inode numbers.
- Dentry has a valid lease or parent directory is complete.
- Security xattrs fit in a single pagelist page.

`ceph_finish_async_create()` fabricates enough inode reply state to instantiate the delegated inode locally, fills the inode, splices it into the dentry, marks `CEPH_I_ASYNC_CREATE`, and finishes open while the MDS request completes asynchronously.

`ceph_async_create_cb()` handles server completion, waking waiters, marking mapping errors, shutting down locally created inodes on failure, and detecting delegated inode mismatches.

## Read Paths

`ceph_read_iter()`:
- Starts read or direct-I/O exclusion.
- Acquires read caps and desired cache/lazy caps.
- Uses direct/sync OSD reads when cache caps are absent, `O_DIRECT` is set, sync mode is forced, or inline data must be fetched.
- Uses `generic_file_read_iter()` with a recorded rw context when cache/lazy caps allow page-cache reads.
- Handles EOF/hole retry by refreshing size.
- Handles inline-data retry by fetching `CEPH_STAT_CAP_INLINE_DATA` and copying inline bytes plus zero-fill.

`__ceph_sync_read()`:
- Flushes dirty page-cache pages in the requested range.
- Splits reads along object and mount boundaries through `ceph_osdc_new_request()`.
- Uses sparse reads for encrypted files or `SPARSEREAD`.
- Adjusts encrypted reads to crypto-block boundaries.
- Treats OSD `-ENOENT` as holes.
- Decrypts sparse encrypted extents.
- Zero-fills short reads before EOF.
- Copies pages into the destination iterator and updates file position.

`ceph_splice_read()` uses `filemap_splice_read()` only when cache/lazy caps allow it; otherwise it falls back to `copy_splice_read()`.

## Write Paths

`ceph_write_iter()`:
- Rejects shutdown and snapshot writes.
- Allocates a cap flush record before taking locks/caps.
- Starts write or direct-I/O exclusion.
- Handles append by refreshing size.
- Runs generic write checks, max file size checks, quota checks, OSD full/nearfull checks, and privilege stripping.
- Acquires write caps plus buffer/lazy caps when useful.
- Updates file time and i_version.
- Chooses sync/direct OSD writes when buffer/lazy caps are absent, direct I/O is requested, sync mode is forced, or previous writes have errored.
- Uses `generic_perform_write()` for buffered writes when file buffer caps permit.
- Marks `FILE_WR` caps dirty after successful writes.
- Retries `-EOLDSNAPC` after dropping cap refs so pending snapshot state can complete.
- Forces dsync behavior when the OSD map or pool is near-full.

`ceph_sync_write()`:
- Flushes page-cache pages in range and invalidates FS-Cache.
- Splits writes by object mapping.
- Adjusts encrypted writes to fscrypt block boundaries.
- Performs read/modify/write for encrypted partial crypto blocks.
- Uses assert-version or exclusive create to protect RMW from concurrent object changes.
- Encrypts page vectors before OSD write.
- Invalidates written page-cache range after successful OSD writes.
- Updates inode size and cap state when extending.

## Direct and Async I/O

`ceph_direct_read_write()`:
- Pins iterator pages into bvec arrays.
- Builds OSD read/write requests with `CEPH_OSD_DATA_TYPE_BVECS`.
- Invalidates page cache and FS-Cache for direct writes.
- Uses sparse read support when requested.
- Allows AIO only when the I/O is within current size or can be satisfied by one OSD request.
- For synchronous direct reads, zero-fills short reads before EOF.
- Returns `-EIOCBQUEUED` after starting queued async OSD requests.

`ceph_aio_complete_req()`:
- Handles per-OSD request completion.
- Retries writes on `-EOLDSNAPC` through workqueue redrive.
- Converts sparse read results, `-ENOENT`, and short reads into user-visible bytes/zero-fill.
- Updates read/write/subvolume metrics.
- Releases pinned bvec pages and completes the aggregate AIO request.

`ceph_aio_complete()`:
- Ends DIO, updates file size for writes, marks write caps dirty, drops cap refs, completes the kiocb, and frees request state when all OSD requests finish.

## Hole Punching and Zeroing

`ceph_fallocate()` supports only `FALLOC_FL_KEEP_SIZE | FALLOC_FL_PUNCH_HOLE`:
- Regular files only.
- Snapshots and encrypted files are rejected.
- Acquires write/buffer caps.
- Invalidates FS-Cache and page cache.
- Zeroes partial page-cache pages and truncates whole cached pages.
- Calls `ceph_zero_objects()` to zero/delete/truncate OSD objects.
- Marks file write caps dirty on success.

`ceph_zero_objects()` maps ranges to object-set boundaries:
- Uses `CEPH_OSD_OP_ZERO` for partial object ranges.
- Uses delete/truncate operations for full object-set coverage.
- Preserves snapshot context by taking the current head or pending capsnap snap context.

## Copy File Range

`ceph_copy_file_range()` first tries `__ceph_copy_file_range()` and falls back to `splice_copy_file_range()` for unsupported or cross-cluster cases.

The OSD copy offload path requires:
- Same Ceph cluster FSID.
- Destination is not a snapshot.
- `NOCOPYFROM` is not set.
- OSDs support copy-from2.
- Non-striped compatible layouts: same stripe unit, stripe count 1, same object size.
- Neither file is encrypted.
- Length is at least one object.
- Source and destination object offsets match.
- Source read caps and destination write/buffer caps are held.
- Source and destination dirty data are written back first.

It handles unaligned leading/trailing partial object regions with `splice_file_range()` and full objects with OSD copy-from requests. Destination page cache and FS-Cache are invalidated, destination size and dirty caps are updated, and OSD `-EOPNOTSUPP` disables future copy-from2 attempts for the mount.

## Metrics and Subvolume Accounting

- Read, write, and copy-from OSD request latencies/sizes update `ceph_client_metric`.
- `ceph_record_subvolume_io()` records nonzero read/write byte counts into subvolume metrics.
- EOF reads are intentionally not counted as subvolume I/O.
- Write metrics count submitted write lengths on successful OSD writes.

## Important Dependencies

- `caps.c`: cap acquisition/release, wanted fmode state, dirty cap marking, cap flush records, snapshot context selection.
- `addr.c`: buffered writeback, inline-data uninlining, mmap preparation, page-cache behavior.
- `cache.c`/`cache.h`: FS-Cache use/unuse and invalidation.
- `crypto.c`/`crypto.h`: encrypted open checks, read/write alignment, encrypted RMW, page encryption/decryption.
- `dir.c`: atomic-open snapdir/notrace helpers and dentry async state.
- OSD client APIs: request allocation, extent setup, sparse reads, copy-from, request wait/callback.
- Linux VFS: generic read/write, direct I/O exclusion, splice, fallocate, llseek, fscrypt, quota/newsize checks.

## Edge Cases and Risks

- Async create depends on delegated inode numbers and local fabricated inode state matching the later MDS reply.
- Direct AIO keeps cap refs until all OSD requests complete; completion paths must release bvec pages and cap refs exactly once.
- Encrypted partial-block sync writes use RMW with object version assertions; version changes force retry.
- Sync/direct reads must distinguish short object reads, holes, EOF, encrypted sparse extents, and copy-to-user faults.
- `-EOLDSNAPC` write retries deliberately drop caps and reacquire snapshot context to preserve snapshot ordering.
- OSD copy offload is conservative; many valid VFS copy cases intentionally fall back to splice to avoid stale size/layout/cap hazards.
- Hole punching encrypted files is disabled because object zeroing would not preserve fscrypt block semantics.
