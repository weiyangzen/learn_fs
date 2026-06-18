# sources/user-network-fs/samba/source3/smbd/smb2_aio.c

## Purpose

`smb2_aio.c` implements shared asynchronous I/O support for smbd, with SMB2-specific read/write scheduling and generic helpers also used by SMB1 AIO paths. It manages lifetime metadata for in-flight operations, attaches tevent requests to `files_struct` objects so close/flush/lock paths can wait for them, and wraps asynchronous writes with optional fsync behavior.

## Important APIs, Types, and Functions

- `aio_write_through_requested(struct aio_extra *aio_ex)`: exposes the write-through flag stored in AIO metadata.
- `create_aio_extra(...)`: allocates `struct aio_extra`, optional output buffer storage, and records the FSP.
- `struct aio_req_fsp_link` plus `aio_add_req_to_fsp(...)` and destructor `aio_del_req_from_fsp(...)`: maintain the dynamic `fsp->aio_requests` array.
- `pwrite_fsync_send`, `pwrite_fsync_recv`: tevent wrapper for async pwrite followed by conditional async fsync.
- `cancel_smb2_aio(struct smb_request *smbreq)`: SMB2 cancel hook that currently never cancels underlying AIO and therefore returns false.
- `schedule_smb2_aio_read(...)`: validates and schedules an SMB2 async read through `SMB_VFS_PREAD_SEND`.
- `schedule_aio_smb2_write(...)`: validates and schedules an SMB2 async write through `pwrite_fsync_send`.
- Completion callbacks `aio_pread_smb2_done` and `aio_pwrite_smb2_done`: translate VFS completion into SMB2 read/write completion.

## Control Flow

Read scheduling validates the requested offset/length, rejects alternate streams and internal opens, checks the configured `aio read size` unless the VFS forces AIO, prevents async execution for non-final compound requests, allocates the read buffer, creates `aio_extra`, checks strict byte-range locks, starts `SMB_VFS_PREAD_SEND`, attaches a completion callback, links the request to `fsp->aio_requests`, and stores `aio_extra` in `smbreq->async_priv`. Completion receives the VFS result, calls `smb2_read_complete`, updates file handle position for positive reads, and completes or errors the SMB2 subrequest.

Write scheduling follows the same shape with write-specific checks: alternate streams/internal opens/minimum size/non-final compound/recvfile unread data are rejected, `write_through` is stored, a write strict-lock range is checked, file modification tracking is prepared, `pwrite_fsync_send` starts the write, the request is linked to the FSP, and level-II oplock contention is signaled. Completion receives write/fsync status, marks the file modified, calls `smb2_write_complete_nosync`, and completes the SMB2 subrequest.

`pwrite_fsync_send` validates the write range, completes immediately for zero-length writes, otherwise starts `SMB_VFS_PWRITE_SEND`. Its write callback stores bytes written and, when `strict sync` and either `sync always` or write-through apply, chains an `SMB_VFS_FSYNC_SEND`; otherwise it completes after the write.

## State and Persistence Behavior

Each AIO request owns an `aio_extra` object for request-private state: FSP, offset, byte count, strict lock descriptor, write-through flag, modification state, and SMB request pointer. `aio_add_req_to_fsp` persists the tevent request pointer in `fsp->aio_requests`; its talloc destructor removes the pointer when the link is freed, shrinking or freeing the array. File close uses this state to mark the FSP closing and wait for in-flight AIO. Successful reads update `fh` position and position information. Successful writes mark the file modified and may persist data through fsync depending on configuration.

## Dependencies and Integration Points

The file depends on tevent request primitives, VFS async read/write/fsync operations, Samba strict locking, SMB2 read/write completion helpers, file-handle position helpers, oplock contention, loadparm settings for AIO and sync behavior, and `files_struct` AIO tracking consumed by close and other smbd operations. Prototypes are exported through `proto.h` and are used by `smb2_read.c`, `smb2_write.c`, SMB1 AIO, flush, ioctl, lock, query-directory, and oplock paths.

## Risks and Edge Cases

The AIO list/destructor relationship is critical: losing the link can make close proceed while I/O is still active; double removal can corrupt `fsp->aio_requests`. `cancel_smb2_aio` intentionally does not cancel underlying work, so callers must continue normal processing and not send a cancel response. Compound requests are restricted to the last element because async completion would otherwise disturb compound response ordering. Write-through correctness depends on `pwrite_fsync_send` honoring strict sync policy. Alternate streams and internal opens fall back to synchronous paths. Range validation and strict-lock checks protect against invalid offsets and lock conflicts before handing control to VFS async backends.

## Test Signals

Coverage should include async read/write above and below configured thresholds, VFS-forced AIO, strict lock conflict denial, non-final compound fallback, alternate stream fallback, internal open fallback, recvfile fallback for writes, zero-length writes, write-through plus strict-sync fsync behavior, close waiting for pending AIO, request-list destructor cleanup, and cancel requests against in-flight SMB2 reads/writes.
