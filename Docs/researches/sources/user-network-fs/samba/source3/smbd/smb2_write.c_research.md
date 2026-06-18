# sources/user-network-fs/samba/source3/smbd/smb2_write.c

## Purpose
This file implements the SMB2 WRITE request path in smbd. It parses SMB2 write packets, validates offsets, data lengths, credit charge, file ids, and server max-write limits, then performs writes to normal files or named pipes using asynchronous paths where possible and synchronous fallback where needed.

## Important APIs, Types, And Functions
The top-level entry point is `smbd_smb2_request_process_write()`. It verifies the request body size, extracts the data offset, data length, offset, persistent and volatile file ids, and write flags, resolves the `files_struct` through `file_fsp_smb2()`, and starts `smbd_smb2_write_send()`.

`smbd_smb2_request_write_done()` receives the tevent completion, builds the SMB2 write response body, writes the byte count, and completes or errors the original SMB2 request.

`struct smbd_smb2_write_state` tracks the request, fake SMB1 request wrapper, target fsp, write-through flag, input length and offset, and output byte count. `smb2_write_complete()` and `smb2_write_complete_nosync()` route into `smb2_write_complete_internal()`, which maps write errors, handles disk-full zero-write behavior, optionally calls `sync_file()`, and stores `out_count`.

`smbd_smb2_write_send()` is the core worker. It handles write-through flag interpretation, fake SMB request creation, named-pipe writes through `np_write_send()`, access checks, POSIX append offset rules, asynchronous file writes through `schedule_aio_smb2_write()`, cancellation through `cancel_smb2_aio()`, strict-lock checks, synchronous `write_file()` fallback, and completion posting.

## Control Flow
The request path first validates the SMB2 wire shape. The data offset must equal the header plus body length, the announced data length must fit in the dynamic input buffer or deferred SMB1 unread bytes for recvfile-style handling, and the length must not exceed `xconn->smb2.server.max_write`. Credit charge is verified against the write length before the file id lookup.

For IPC/named pipes, `smbd_smb2_write_send()` requires a pipe fsp, sends the buffer to `np_write_send()`, marks async activity on the fsp with `aio_add_req_to_fsp()`, and completes in `smbd_smb2_write_pipe_done()`. Pipe errors are mapped through `nt_status_np_pipe()`, and zero writes for nonzero input are treated as access denied.

For normal files, the function checks `FILE_WRITE_DATA|FILE_APPEND_DATA`, validates the special append offset against `fsp->fsp_flags.posix_append`, and tries `schedule_aio_smb2_write()`. `NT_STATUS_OK` means the AIO layer owns completion and cancellation is enabled. Any status other than `NT_STATUS_RETRY` is a setup failure. `NT_STATUS_RETRY` falls back to synchronous I/O after `SMB_VFS_STRICT_LOCK_CHECK()`.

## State And Persistence Behavior
Persistent state changes are the bytes written to the target file or pipe. The path also updates normal smbd file-modified state indirectly through `write_file()` or AIO completion code, and it may force data to stable storage with `sync_file()` when write-through or SMB 3.0.2 unbuffered flags request it.

The tevent request state is transient and owns the fake `smb_request`. Cancellation is available only for scheduled SMB2 AIO writes. IPC writes attach async state to the fsp to protect shutdown/close handling while a pipe write is outstanding.

## Dependencies And Integration Points
This file integrates with SMB2 request framing, credit accounting, `file_fsp_smb2()` open lookup, smbd fake SMB1 request creation, access checks from `smb2_trans2.c`, named-pipe helpers, AIO scheduling/cancellation, strict byte-range locking, `write_file()`, sync/write-through handling, and server connection termination on transport errors.

It also depends on `smbd_smb2_request_pending_queue()` for asynchronous response lifetime and uses the generic tevent request model used throughout smbd.

## Risks And Edge Cases
Important correctness risks include accepting malformed data offsets, overrun of the dynamic buffer, exceeding negotiated max write, mishandling recvfile-style NULL input data, incorrect credit charge verification, or returning success for zero bytes written when the client sent data.

Concurrency risks involve strict-lock enforcement on the synchronous fallback and cancellation semantics for AIO. Append mode is intentionally strict: POSIX-append handles must use `VFS_PWRITE_APPEND_OFFSET`, and non-append handles must not. Write-through behavior must remain aligned with protocol flags because it affects durability guarantees and performance.

## Test Signals
Useful tests include SMB2 write torture cases for max-write negotiation, credit charge boundaries, invalid data offsets, invalid file ids, byte-range lock conflicts, append-only behavior, write-through/unbuffered writes, AIO cancellation, disk-full behavior, alternate-stream `EOVERFLOW` mapping to `NT_STATUS_FILE_SYSTEM_LIMITATION`, named-pipe writes, and recvfile/large-write paths.
