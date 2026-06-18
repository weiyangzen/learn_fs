# sources/user-network-fs/samba/source3/smbd/smb2_read.c

## Purpose
This file implements SMB2 READ handling for regular files and IPC named pipes. It validates read requests, enforces maximum read and credit charge rules, dispatches named-pipe reads asynchronously, tries VFS AIO for file reads, falls back to strict-lock-checked synchronous reads, and can use a sendfile fast path when the response can be sent directly from the file to the socket.

## Important APIs, Types, And Functions
The request entry point is `smbd_smb2_request_process_read()`. Async file logic lives in `smbd_smb2_read_send()`/`recv()` and `struct smbd_smb2_read_state`. Completion and error normalization are handled by `smb2_read_complete()`. Sendfile setup and transfer use `schedule_smb2_sendfile_read()` and `smb2_sendfile_send_data()`, with fallback helpers `fake_sendfile()` and `sendfile_short_send()` from the reply helper file. Named pipes use `np_read_send()`/`np_read_recv()` and cancellation through `smbd_smb2_read_ipc_cancel()`. File AIO cancellation calls `cancel_smb2_aio()`.

## Control Flow
The top-level parser verifies the 0x31-byte body, reads SMB3 flags when applicable, checks `max_read`, verifies credit charge, resolves the volatile/persistent file id, starts `smbd_smb2_read_send()`, and queues the request pending. The send path rejects directories, creates a fake SMB request, routes IPC handles to `np_read_send()` with an fsp async link, checks file read access, tries `schedule_smb2_aio_read()`, falls back to strict byte-range lock checking, tries sendfile if signing, encryption, compounding, streams, file type, offset, and file size permit it, and otherwise reads into a talloc data blob with `read_file()`. The done callback builds the SMB2 read response body and dynamic data blob.

## State And Persistence
The operation is read-only for file contents, but it creates transient tevent state, pipe subrequests, fsp AIO links, output blobs, and sendfile queue metadata. The sendfile path deliberately transfers ownership of the read state to the SMB2 send queue and uses a destructor to perform socket I/O after headers are built. No persistent Samba database state is updated.

## Dependencies And Integration Points
This file integrates SMB2 request/response helpers, file-id lookup, access macros, strict locking, VFS AIO and sendfile hooks, named-pipe RPC handles, cancellation infrastructure, talloc lifetimes, and lower-level socket write helpers. It also depends on server signing/encryption/compound state to decide whether zero-copy sendfile is legal.

## Risks And Test Signals
Tests should cover max-read and credit violations, closed handles, directory read rejection, access denied, strict lock conflict, zero-length reads, EOF versus minimum-count behavior, AIO success/cancel/error, named-pipe success/cancel/broken pipe/status mapping, sendfile eligibility exclusions, sendfile `ENOSYS`/`ENOTSUP`/`EINTR` fallback, file truncation during sendfile causing zero-fill, and torture body padding. Risks include wrong lifetime for sendfile state, sending data on encrypted or signed requests, returning EOF too aggressively for pipe reads, and failing to detach outstanding async activity during close.
