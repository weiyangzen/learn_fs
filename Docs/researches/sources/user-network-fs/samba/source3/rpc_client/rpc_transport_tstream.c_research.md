# sources/user-network-fs/samba/source3/rpc_client/rpc_transport_tstream.c

## Purpose
`rpc_transport_tstream.c` implements the generic `rpc_cli_transport` callbacks on top of Samba `tstream_context`. It provides queued asynchronous reads, writes, timeout handling, connection checks, and an SMB named-pipe transact optimization.

## Important APIs, Types, And Functions
Public functions are `rpc_transport_tstream_init()` and `rpc_transport_get_tstream()`. Internal state `rpc_tstream_state` owns the stream, read queue, write queue, and timeout. Callback implementations are `rpc_tstream_read_send/recv()`, `rpc_tstream_write_send/recv()`, `rpc_tstream_trans_send/recv()`, `rpc_tstream_is_connected()`, and `rpc_tstream_set_timeout()`.

## Control Flow
Initialization creates a transport, state, read/write tevent queues, moves in the caller's stream, sets a 10-second default timeout, installs read/write callbacks, and enables transact callbacks only when `tstream_is_smbXcli_np()` is true. Reads use `tstream_readv_pdu_queue_send()` with a one-vector provider capped at `UINT16_MAX`. Writes use `tstream_writev_queue_send()`. Both set endtimes and disconnect the stream on lower-level failure.

`rpc_tstream_trans_send()` checks whether the stream is connected and whether both queues are empty; only then does it ask SMB named-pipe tstream to use transact. It starts write and read requests in parallel on the respective queues, reads up to `max_rdata_len`, and returns the reply buffer.

## State And Persistence
State is runtime-only and talloc-owned under the transport. Failures free the stream to mark disconnection. Timeout is stored in milliseconds and may also be propagated to SMB named-pipe tstreams.

## Dependencies And Integration Points
Dependencies include tevent queues, tstream APIs, SMB named-pipe tstream helpers, NTSTATUS/unix error mapping, and `cli_pipe.c`. It is the common backend for socket and named-pipe transports.

## Risks
The read vector caps a single read to `UINT16_MAX`, so higher layers must be prepared for short reads. In the transact receive path, `rep.iov_len` remains the requested max length rather than the actual byte count returned by `tstream_readv_pdu_queue_recv()`, which is a subtle contract worth checking against consumers. Endtime setup failures return a posted request without an explicit error in some paths. Disconnection is represented by freeing the stream, so callbacks must not use stale stream pointers after an error.

## Test Signals
Tests should cover queued concurrent read/write ordering, timeout expiry, disconnect detection for SMB named pipes and generic streams, short read handling, transact use only when queues are empty, reply length correctness, and `set_timeout()` behavior on connected and disconnected streams.
