# sources/user-network-fs/samba/source3/smbd/smb1_ipc.c

## Purpose

`smb1_ipc.c` implements SMB1 `SMBtrans` and `SMBtranss` handling for IPC named-pipe and mailslot-style transaction paths. It assembles multi-packet transaction requests, dispatches LANMAN or named-pipe operations, performs async DCE/RPC write/read cycles on pipe handles, and fragments transaction replies according to the negotiated SMB1 max send size.

## Important APIs, Types, And Functions

- `send_trans_reply()` sends one or more SMBtrans reply packets with parameter/data offsets and optional buffer-overflow status.
- `reply_trans()` parses the primary SMBtrans request, allocates a `trans_state`, copies initial params/data/setup, and either waits for secondary packets or dispatches.
- `reply_transs()` handles secondary SMBtrans packets and dispatches when all bytes arrive.
- `handle_trans()` validates `\PIPE` names and routes to `named_pipe()`.
- `named_pipe()` routes `LANMAN` to `api_reply()` and known pipe names or empty names to `api_fd_reply()`.
- `api_fd_reply()` validates pipe handle/VUID and dispatches pipe subcommands.
- `api_dcerpc_cmd()` writes request data to a named pipe and asynchronously reads the response.
- `api_dcerpc_cmd_write_done()` and `api_dcerpc_cmd_read_done()` complete the pipe I/O.
- `api_WNPHS()`, `api_SNPHS()`, and `api_no_reply()` handle minor pipe commands or unsupported calls.

Important local state includes `struct dcerpc_cmd_state` and the externally defined `struct trans_state`.

## Control Flow

`reply_trans()` validates word count and offsets, rejects duplicate/invalid transaction state through `allow_new_trans()`, allocates request buffers with 100 bytes of zero slack for legacy core routines, parses setup words, and either stores incomplete state in `conn->pending_trans` with an interim response or calls `handle_trans()`. `reply_transs()` finds the matching pending transaction by MID, optionally shrinks totals if the client revised them downward, validates displacement/count ranges with `smb_buffer_oob()`, copies bytes into the accumulated buffers, and dispatches once complete.

`handle_trans()` accepts WinCE-style local-machine prefixes, requires a `\PIPE` path, normalizes optional slash behavior, and calls `named_pipe()`. `named_pipe()` treats `LANMAN` as the old RAP/LANMAN API path; selected pipe names from Win9x are routed through an already-open pipe handle path; empty names also use fd dispatch. After dispatch, `close_on_completion` can disconnect the tree connection and free the tcon.

For DCE/RPC pipe commands, `api_fd_reply()` validates setup count, file handle, named-pipe type, and VUID. `api_dcerpc_cmd()` rejects concurrent pipe reads, copies request data, sends `np_write_send()`, then reads up to the requested max with `np_read_send()`. Completion maps named-pipe NTSTATUS values with `nt_status_np_pipe()`, sends errors directly, or uses `send_trans_reply()` with `is_data_outstanding` as the buffer-overflow/more-data signal.

## State And Persistence Behavior

The module stores incomplete transactions on `conn->pending_trans` and owns malloc-allocated param/data buffers until completion or error. Async DCE/RPC state is attached to `req->async_priv` and the request is moved under the connection until callbacks finish. It mutates tree-connect state when `close_on_completion` is set. It does not persist data itself; named-pipe I/O talks to the RPC pipe subsystem and connection/session state.

## Dependencies And Integration Points

Dependencies include SMB1 request/reply helpers, transaction state management, named-pipe fake file handles, RPC pipe handlers, LANMAN `api_reply()`, profile macros, security/encryption send flags, file lookup by FID, SMBX tcon disconnect, and buffer-boundary helpers. It integrates with SMB1 command dispatch and with the source3 RPC server pipe machinery.

## Risks

SMBtrans parsing is boundary-sensitive. Incorrect offsets, displacements, or revised totals can corrupt buffers; this file uses `smb_buffer_oob()` guards before copies. Memory ownership is mixed between talloc and `SMB_MALLOC`, so every bad-parameter path must free both correctly. Async pipe requests require careful request lifetime management. `send_trans_reply()` fragments by `max_send` with a fixed overhead hack; regressions can break old SMB1 clients. `close_on_completion` disconnects the tcon after dispatch and exits the server on disconnect failure, so outstanding request cancellation remains a TODO risk.

## Test Signals

Tests should cover complete primary transactions, multi-packet primary/secondary assembly, duplicate MID rejection, offset/displacement OOB rejection, downward total revision, LANMAN routing, `\PIPE` prefix normalization, unknown pipe rejection, invalid pipe handle/VUID, DCE/RPC write/read success, pipe busy, pipe error mapping, more-data/buffer-overflow replies, fragmented replies under small max-send values, and close-on-completion tcon disconnect.
