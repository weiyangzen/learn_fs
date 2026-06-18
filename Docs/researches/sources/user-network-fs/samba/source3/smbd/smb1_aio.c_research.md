# sources/user-network-fs/samba/source3/smbd/smb1_aio.c

## Purpose

`smb1_aio.c` schedules and completes asynchronous SMB1 ReadX and WriteX operations using the VFS async interfaces and tevent callbacks. It builds SMB1 replies ahead of time, holds strict-lock context for the operation, tracks outstanding requests on the file handle, updates file offsets/modification state, and sends the final SMB1 response when the async operation completes.

## Important APIs, Types, And Functions

- `schedule_aio_read_and_X()` validates and schedules an async pread for SMB1 ReadX.
- `aio_pread_smb1_done()` completes the pread, builds success/error response, updates file position, and sends the reply.
- `schedule_aio_write_and_X()` validates and schedules async pwrite/fsync work for SMB1 WriteX.
- `aio_pwrite_smb1_done()` completes the write, marks file modified, handles write-behind semantics, and sends the reply when required.

The code uses `struct aio_extra`, `struct smb_request`, `files_struct`, `connection_struct`, strict-lock structs, `vfs_aio_state`, and VFS async request APIs.

## Control Flow

Read scheduling rejects invalid ranges, alternate streams, reads below `aio read size` unless forced, and chained SMB requests. It allocates `aio_extra` with enough output buffer space, constructs a fixed SMB1 ReadX reply, initializes a read strict lock, checks the lock, records byte count and offset, starts `SMB_VFS_PREAD_SEND()`, attaches the callback, adds the tevent request to the file's AIO list, moves ownership of the SMB request under `aio_extra`, and returns `NT_STATUS_OK`.

Read completion receives the VFS result, handles the file-closed-while-outstanding case, maps errors to SMB status, or calls `setup_readX_header()` on success and updates file position. It sets the NetBIOS length, logs/shows the message, sends through `smb1_srv_send()`, and frees `aio_extra`.

Write scheduling follows similar gating for streams, minimum size, and chains. It constructs a WriteX reply, initializes a write strict lock, prepares modified state, sends `pwrite_fsync_send()`, records the request, triggers level2 oplock contention hooks, and optionally sends an immediate success reply for write-behind when not write-through, not `sync always`, and `aio_write_behind` is set.

Write completion receives the write/fsync result, handles closed files, marks the file modified, logs write-behind errors without notifying the client, or builds/sends normal success/error/disk-full responses.

## State And Persistence Behavior

The module keeps per-operation state in `aio_extra` and outstanding tevent requests linked to `fsp` by `aio_add_req_to_fsp()`. It updates file handle position and position-information state after successful reads/writes and marks modification state for writes. It does not persist metadata directly; persistence happens through the VFS write/fsync path. Write-behind can acknowledge before data durability is known.

## Dependencies And Integration Points

Dependencies include SMB1 reply builders, VFS async read/write/fsync functions, strict locking, AIO request tracking, oplock contention hooks, file-handle position helpers, error mapping, encryption checks, and server exit on send failure. It integrates with SMB1 ReadX/WriteX handlers that fall back to synchronous behavior on `NT_STATUS_RETRY`.

## Risks

Write-behind is explicitly risky: later errors are logged as potential corruption and the TODO notes success should not be returned on error. Strict locks are checked at scheduling time and held conceptually until completion; incorrect lifetime can violate locking. Chained SMB requests are rejected to avoid complex reply ordering. The file-closed callback path drops the reply, so higher layers must tolerate closed handles with outstanding AIO. Send failure exits the server cleanly.

## Test Signals

Tests should cover minimum-size retry, forced AIO, alternate-stream retry, chained-request retry, invalid read range, strict-lock conflict, allocation failure, VFS send failure fallback, read success/error response formatting, partial write disk-full mapping, write-through/fsync behavior, write-behind early reply and later error logging, closed-file completion, encrypted connection send flag, and file-position updates.
