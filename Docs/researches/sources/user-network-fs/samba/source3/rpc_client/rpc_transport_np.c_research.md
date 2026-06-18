# sources/user-network-fs/samba/source3/rpc_client/rpc_transport_np.c

## Purpose
`rpc_transport_np.c` initializes an RPC transport over an SMB named pipe by opening the pipe on an existing `cli_state` connection and wrapping the resulting `tstream` in the common RPC transport abstraction.

## Important APIs, Types, And Functions
Exports are `rpc_transport_np_init_send()` and `rpc_transport_np_init_recv()`. Internal state `rpc_transport_np_init_state` tracks the chosen SMB session/tree, pid for SMB1, connection, timeout, absolute timeout, pipe name, retry count, event context, and final `rpc_cli_transport`.

## Control Flow
The send function selects SMB2 or SMB1 session/tcon fields from `cli_state`, strips leading backslashes from the pipe name, computes an absolute timeout, and starts `tstream_smbXcli_np_open_send()`. Completion receives a `tstream_context`. If the server returns `NT_STATUS_PIPE_NOT_AVAILABLE` before timeout expiry, it schedules a retry timer with increasing delay, matching Windows on-demand pipe server behavior. On success it calls `rpc_transport_tstream_init()` and completes.

## State And Persistence
State is per-request only. It does not persist anything, but it relies on the existing SMB connection/session/tree state staying alive for the transport.

## Dependencies And Integration Points
Dependencies include tevent NTSTATUS helpers, SMBX client base, named-pipe tstream helpers, `cli_state`, and `rpc_transport_tstream_init()`. It is used by generic RPC pipe setup and WSP client code for named-pipe RPC.

## Risks
Retry delay starts at `100 * retries` milliseconds while `retries` is incremented after scheduling, so the first retry can be immediate. The absolute timeout derives from `cli->timeout`; incorrect timeout values can cause too many retries or premature failure. Lifetime depends on the underlying SMB objects. Pipe-name normalization mutates the talloc string pointer by advancing past backslashes, so only the normalized pointer is retained.

## Test Signals
Tests should cover SMB1 and SMB2 pipe opens, leading backslash normalization, pipe-not-available retry until success, timeout expiry, constructor cleanup on open failure, and successful transact-enabled RPC over the returned transport.
