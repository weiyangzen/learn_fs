# sources/user-network-fs/samba/source3/smbd/smb1_pipes.h

## Purpose
`smb1_pipes.h` declares the SMB1 named-pipe reply routines implemented in `smb1_pipes.c`. It is the narrow interface by which the broader SMB1 reply/dispatch code invokes pipe-specific open, read, and write handlers.

## Important APIs, types, and functions
- `reply_open_pipe_and_X(connection_struct *conn, struct smb_request *req)` opens a named pipe from an OpenAndX request and formats the pipe-specific OpenAndX response.
- `reply_pipe_write_and_X(struct smb_request *req)` handles async AndX pipe writes.
- `reply_pipe_read_and_X(struct smb_request *req)` handles async AndX pipe reads.
- `reply_pipe_write(struct smb_request *req)` handles the older non-AndX SMB pipe write form.

## Control flow
This header has no executable control flow. Its prototypes allow SMB1 reply code to dispatch pipe operations without exposing the callback state structs or helper functions used internally by `smb1_pipes.c`.

## State and persistence behavior
The header defines no state. State is carried through `connection_struct`, `struct smb_request`, `files_struct`, and named-pipe handles owned by the implementation and surrounding smbd subsystems.

## Dependencies and integration points
The declarations depend on Samba's smbd types being visible to includers, especially `connection_struct` and `struct smb_request`. The main integration point is SMB1 command dispatch in files such as `smb1_reply.c`, which detects IPC named-pipe operations and calls these functions. Completion is integrated with `smb_request_done()` and `smb1_srv_send()` declared from the SMB1 processing layer.

## Risks and edge cases
- There are no include guards or local includes in this header fragment; it relies on the existing Samba include discipline.
- The interface exposes only request-level entry points, so callers must already have parsed enough SMB state to choose the pipe path correctly.
- Since the functions may suspend requests asynchronously, callers must honor the `req->outbuf == NULL` convention used by SMB1 processing.

## Test signals
Header-level test signals are compile/link coverage: all pipe reply callers should build with the declared signatures. Behavioral tests belong to `smb1_pipes.c` and should verify that these entry points interoperate with SMB1 command dispatch, chained request completion, and named-pipe RPC traffic.
