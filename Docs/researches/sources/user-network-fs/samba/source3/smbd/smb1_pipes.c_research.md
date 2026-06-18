# sources/user-network-fs/samba/source3/smbd/smb1_pipes.c

## Purpose
`smb1_pipes.c` implements SMB1 named-pipe reply routines for the smbd server. It handles opening IPC named pipes via `SMBopenX` pipe paths and adapts SMB1 pipe read/write commands into the asynchronous named-pipe server API used for RPC-over-SMB.

## Important APIs, types, and functions
- `reply_open_pipe_and_X(connection_struct *conn, struct smb_request *req)` parses an incoming `\PIPE\...` name, validates the pipe namespace, opens the pipe with `open_np_file()`, and formats the SMB1 OpenAndX response for a message-mode named pipe.
- `reply_pipe_write_and_X(struct smb_request *req)` handles `SMBwriteX` requests directed at named pipes, including the `PIPE_START_MESSAGE | PIPE_RAW_MODE` quirk where the first two client bytes are treated as an untrusted PDU-length field and skipped.
- `pipe_write_andx_done()` receives the async `np_write_send()` result, verifies the full payload was written, builds the WriteAndX reply, and completes the request with `smb_request_done()`.
- `reply_pipe_read_and_X(struct smb_request *req)` builds a read reply buffer up front, detaches `req->outbuf` to mark the SMB request async, and starts `np_read_send()` into the SMB output data area.
- `pipe_read_andx_done()` maps named-pipe status via `nt_status_np_pipe()`, restores the detached output buffer, sizes the SMB response, and fills the read count and data offset.
- `reply_pipe_write(struct smb_request *req)` and `pipe_write_done()` provide the older non-AndX write path, using `np_write_send()` and then sending directly through `smb1_srv_send()`.
- Small state structs (`pipe_write_andx_state`, `pipe_read_andx_state`, `pipe_write_state`) keep request-local async metadata under `req->async_priv`.

## Control flow
The open path pulls the pipe name from the request byte buffer with `srvstr_pull_req_talloc()`, strips leading backslashes, requires the `PIPE\` prefix, and passes the remaining pipe endpoint name to `open_np_file()`. A missing pipe maps to the DOS `ERRbadpipe` compatibility error, while other open failures return the NT status. Success creates a 15-word OpenAndX reply, marks the object as an existing message-mode named pipe, and returns the new file number.

The write paths validate that the FID resolves to a named-pipe `files_struct` and that the file was opened by the same VUID as the request. They allocate per-request state, locate the client payload in the SMB request, and start an async named-pipe write against `fsp->fake_file_handle`. Completion callbacks own the suspended `smb_request` after `talloc_move(req->conn, &req)`. The AndX callback uses `smb_request_done()` so the request can participate in normal chained-response handling; the legacy write callback calls `smb1_srv_send()` itself and frees the request.

The read path similarly validates the pipe handle and VUID, allocates the maximum-sized SMB output buffer immediately, and passes the final data area to `np_read_send()`. Detaching `req->outbuf` is the signal to higher SMB1 processing that the request has suspended. The callback restores and resizes the output buffer once the named-pipe server returns data.

## State and persistence behavior
This file does not persist state outside the live smbd connection. It mutates transient request state (`req->async_priv`, `req->outbuf`, request ownership), uses the open file table via `file_fsp()`, and operates on the named-pipe fake file handle stored in `files_struct`. Opened named pipes persist only as smbd file handles and underlying RPC pipe state managed by the named-pipe server layer.

## Dependencies and integration points
The file depends on core smbd request/buffer helpers, `files_struct` handle lookup, Samba's `talloc` ownership model, `tevent_req` async callbacks, SMB1 wire helpers (`SSVAL`, `SVAL`, `smb_buf`, `reply_smb1_outbuf`), named-pipe helpers from `rpc_server/srv_pipe_hnd.h`, and pipe status mapping from DCERPC support. It is called from SMB1 reply dispatch for pipe-specific `openX`, `readX`, and `write` handling, and it calls back into `smb_request_done()`/`smb1_srv_send()` from `smb1_process.c` to ship replies.

## Risks and edge cases
- Pointer-derived payload locations (`smb_doff`, `req->buf + 3`) trust earlier SMB request validation; malformed offsets are dangerous if upstream bounds checks regress.
- The `PIPE_START_MESSAGE | PIPE_RAW_MODE` path subtracts two bytes only after checking length; this is important for underflow and protocol-compatibility behavior.
- Async ownership is delicate: AndX callbacks rely on `smb_request_done()` after moving `req` under the connection, while the legacy callback sends and frees manually.
- Write completion treats partial writes as errors, including a legacy `ACCESS_DENIED` mapping that comments already question.
- The read path allocates `smb_maxcnt + 1` bytes in the output buffer before async completion, so maximum-count validation in request parsing matters.
- The disabled `STATUS_BUFFER_OVERFLOW` branch notes unresolved interaction with chained error fixups; changing this may affect clients that expect more-data signaling.

## Test signals
Relevant signals are SMB1/IPC integration tests that open `\\PIPE\\...`, issue RPC traffic over `SMBwrite`, `SMBwriteX`, and `SMBreadX`, and exercise chained AndX behavior. Regression coverage should include invalid pipe names, wrong VUID handles, short raw-message writes, partial named-pipe write failures, read responses with outstanding pipe data, and encrypted/signed connections where the final send path is owned by `smb1_process.c`.
