# sources/user-network-fs/samba/source3/smbd/smb1_aio.h

## Purpose

`smb1_aio.h` declares the SMB1 asynchronous ReadX and WriteX scheduling entry points implemented by `smb1_aio.c`. It is the narrow interface used by SMB1 command handling code to attempt async I/O and fall back to normal synchronous handling when async scheduling is not applicable.

## Important APIs, Types, And Functions

The header exports:

- `NTSTATUS schedule_aio_read_and_X(connection_struct *conn, struct smb_request *req, files_struct *fsp, off_t startpos, size_t smb_maxcnt);`
- `NTSTATUS schedule_aio_write_and_X(connection_struct *conn, struct smb_request *req, files_struct *fsp, const char *data, off_t startpos, size_t numtowrite);`

The declarations depend on `connection_struct`, `struct smb_request`, `files_struct`, `off_t`, `size_t`, and `NTSTATUS` types provided by the broader smbd include environment.

## Control Flow

This header has no executable control flow. Its integration contract is status-driven: callers invoke a scheduler during SMB1 ReadX/WriteX processing. `NT_STATUS_OK` means the request ownership has moved into async state and a later callback will send the SMB1 reply. `NT_STATUS_RETRY` means async was declined and the caller should use the synchronous path. Other errors such as invalid parameter, no memory, or file-lock conflict can be returned directly to the client.

## State And Persistence Behavior

The header owns no state. Its prototypes imply that the implementation may take ownership of `req` on success and may write data through VFS async mechanisms for writes. Callers must not assume the request remains available after successful scheduling.

## Dependencies And Integration Points

The header integrates SMB1 command dispatch with the async implementation. It should be included only where the smbd core types are already visible. Its main dependency is the ABI consistency with `smb1_aio.c`; parameter order and ownership expectations are part of the implicit contract.

## Risks

The largest risk is caller misuse of the status/ownership contract. Treating `NT_STATUS_OK` as if a reply still needs to be sent synchronously would duplicate responses, while using `req` after successful scheduling could become a lifetime bug. Adding parameters or changing return semantics requires auditing SMB1 ReadX/WriteX callers.

## Test Signals

Build tests should catch prototype drift. Behavioral tests should assert that SMB1 ReadX/WriteX callers fall back on `NT_STATUS_RETRY`, return immediate errors for hard failures, and do not send duplicate replies after `NT_STATUS_OK`.
