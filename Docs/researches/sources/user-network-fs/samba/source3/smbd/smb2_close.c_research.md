# sources/user-network-fs/samba/source3/smbd/smb2_close.c

## Purpose

`smb2_close.c` implements SMB2 CLOSE request processing. It validates the close packet, resolves the open file id, waits for in-flight AIO when needed, handles delete-on-close lease-break delay, closes and frees the FSP, and optionally returns full file information captured around close.

## Important APIs, Types, and Functions

- `smbd_smb2_request_process_close(struct smbd_smb2_request *req)`: parses SMB2 CLOSE, resolves the FSP, starts async close processing, and queues the request pending.
- `smbd_smb2_close_send/recv`: tevent wrapper around close state, AIO waiting, lease-break delay, and output metadata capture.
- `smbd_smb2_request_close_done(...)`: builds the 0x3c SMB2 CLOSE response body from close state.
- `smbd_smb2_close(...)`: performs the actual close via a fake SMB request, `close_file_smb`, optional full-info collection, and `file_free`.
- `setup_close_full_information(...)`: marshals timestamps, allocation size, EOF, and close flags from `smb_filename` stat data.
- `smbd_smb2_close_wait_done(...)`: resumes close after pending AIO requests drain.
- `smbd_smb2_close_delay_lease_break_done(...)`: resumes close after waiting for a handle lease break and restores user/service context.
- `struct smbd_smb2_close_state`: holds input FSP/flags, output metadata, and optional wait queue.

## Control Flow

The request entry validates a 0x18 body, reads close flags and file ids, resolves the FSP with `file_fsp_smb2`, and starts `smbd_smb2_close_send`. The send helper marks the FSP closing, tries to cancel each tracked AIO request, and if any remain creates a tevent queue that completes only after all AIO request destructors remove their waiters. When the wait completes, `smbd_smb2_close_wait_done` calls the real close.

If there is no pending AIO but `initial_delete_on_close` is set, the send helper checks share mode state. If delete-on-close is not already set, it delays for a handle lease break up to `OPLOCK_BREAK_TIMEOUT`; synchronous completion falls through, and asynchronous completion resumes in `smbd_smb2_close_delay_lease_break_done` after restoring the session's user/service context.

The actual close creates a fake SMB request, optionally records DOS attributes and sets `fstat_before_close` for full-information responses, calls `close_file_smb`, then uses still-available `fsp->fsp_name` stat data to fill full information before `file_free`. The completion callback receives state, generates the response body, serializes times using the connection timestamp resolution, and calls `smbd_smb2_request_done`.

## State and Persistence Behavior

The FSP is marked `closing` before waiting, preventing later lookup/use as an active handle. `close_file_smb` and `file_free` remove open-file state, release share modes, and finalize filesystem side effects such as delete-on-close. `fsp->aio_requests` controls whether close must wait for asynchronous operations started by `smb2_aio.c` or related paths. Full close information is copied into the close state before the FSP is freed. Delete-on-close lease-delay logic reads and updates behavior through share mode locks and lease-break handling.

## Dependencies and Integration Points

The file integrates with SMB2 server dispatch, SMB2 request body helpers, FSP lookup by SMB2 file id, fake SMB request creation, `close_file_smb`, `file_free`, AIO tracking on `files_struct`, tevent queues, share mode locks, handle lease-break delay helpers, user/service context switching, DOS attribute/stat helpers, allocation-size VFS calls, and timestamp conversion. Its AIO wait semantics depend on `aio_add_req_to_fsp` destructors from `smb2_aio.c`.

## Risks and Edge Cases

Close must not free an FSP while AIO callbacks still reference it; the wait-queue and `fsp->aio_requests` destructor protocol is the key safety mechanism. The loop that cancels AIO requests only advances when cancellation fails, relying on successful cancellation to remove entries. Full-information responses depend on stat data being available after `close_file_smb` but before `file_free`. Delete-on-close handling must not race lease break acknowledgement or lose user context after asynchronous delay. On close failure, the code frees the FSP with `file_free`, so callers must treat the handle as consumed even on some errors.

## Test Signals

Test coverage should include basic close, close of already closed file ids, full-information close for files and directories, DOS filetime resolution behavior, pending AIO close waits, cancellable and non-cancellable AIO requests, delete-on-close with and without existing share mode delete state, handle lease-break delay timeout/success, user-context restoration after delay, close failure paths, and response serialization of 0x3c body fields.
