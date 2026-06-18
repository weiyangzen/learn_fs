# File Research: sources/os/linux/linux/fs/smb/client/transport.c

## Scope
Read completely: 1,291 lines. This file implements core SMB client transport mechanics: socket/RDMA sends, request credit reservation, MID allocation lifecycle integration, compound send/receive, cancellation, response waiting, channel selection, and large read response handling.

## Purpose
`transport.c` is the generic send/receive layer below SMB1 and SMB2/3 operation code. Higher-level protocol helpers build `struct smb_rqst` arrays, then this layer reserves credits, creates pending MID entries, serializes signing/sending under server locking, waits for demultiplexed responses, transfers response buffer ownership, and cleans up MIDs.

## Main Interfaces
- MID lifecycle: `cifs_wake_up_task()`, `__release_mid()`, `delete_mid()`.
- Sending: `smb_send_kvec()`, `smb_rqst_len()`, `__smb_send_rqst()`, internal `smb_send_rqst()`.
- Credits and waits: `wait_for_free_request()`, `wait_for_response()`, `cifs_wait_mtu_credits()`.
- Async calls: `cifs_call_async()`.
- Sync result handling: `cifs_sync_mid_result()`.
- Channel selection: `cifs_pick_channel()`.
- Sync/compound calls: `compound_send_recv()`, `cifs_send_recv()`.
- Receive discard/read path: `cifs_discard_remaining_data()`, `cifs_readv_receive()`.

## Send Path
`__smb_send_rqst()` handles the physical send path:
- Uses SMB Direct/RDMA via `smbd_send()` when enabled.
- Checks missing socket and fatal pending signals before starting.
- Corks TCP while sending the RFC1002 marker plus all request vectors/iter payloads.
- Blocks signals while the packet is being sent to avoid partial sends caused by interrupted syscall context.
- Sends the 4-byte RFC1002 length marker, then request kvecs, then optional iterator data.
- Uncorks TCP and signals reconnect on partial sends so the server discards incomplete SMB frames.
- Normalizes most socket send errors to `-ECONNABORTED` and requests reconnect.

`smb_send_kvec()` performs the low-level `sock_sendmsg()` loop with retry behavior:
- Uses `MSG_DONTWAIT` when `server->noblocksnd` is set.
- Retries `-EAGAIN` and `-EINTR` with pending task work.
- Bounds retry time to about 15 seconds.
- Treats zero-byte sends as retryable but unusual.

`smb_send_rqst()` wraps this for compression and encryption:
- `CIFS_COMPRESS_REQ` delegates to `smb_compress()`.
- Plain requests go directly to `__smb_send_rqst()`.
- `CIFS_TRANSFORM_REQ` prepends an SMB3 transform header, calls dialect `init_transform_rq`, sends the transformed compound, then frees transformed request state.

## Credit Handling
`wait_for_free_credits()` reserves credits before sending:
- Selects the relevant credit field with `server->ops->get_credits_field()`.
- Nonblocking operations, especially oplock breaks, can consume a credit immediately.
- Blocking waiters sleep on `server->request_q` until enough credits are available or timeout/signal/exiting state occurs.
- Single-credit normal requests avoid starving compounds by reserving the last `MAX_COMPOUND` credits when many requests are already in flight.
- Reconnect instance is returned to callers so stale credits can be detected before send.

`wait_for_compound_request()` handles multi-request compounds:
- If insufficient credits and nothing is in flight, returns `-EDEADLK` rather than waiting forever.
- Otherwise waits up to 60 seconds for the compound credit set.

The generic `cifs_wait_mtu_credits()` stub simply reports one byte count as the transfer size and zero explicit credits; SMB2/3 dialect code overrides large-MTU credit accounting elsewhere.

## MID And Response Flow
`cifs_call_async()`:
- Reserves or consumes existing credits.
- Locks the server send path.
- Rejects credits from an old reconnect instance.
- Calls dialect `setup_async_request()`.
- Enqueues the MID on `pending_mid_q`, sets callbacks/state, saves send time, sends the request, and rolls back MID/sequence state on failure.

`compound_send_recv()`:
- Initializes response buffer types.
- Validates session/server state and reserves credits for all compound parts.
- Serializes setup and send under `cifs_server_lock()`.
- Sets up one MID per request, with callbacks that return credits for each part and wake the caller only on the last response.
- Sends all requests as one compound.
- Updates SMB3.1.1 preauth hash for negotiate/session setup traffic.
- Waits for all MID responses.
- On interrupted wait, sends CANCEL requests and installs cancellation callbacks.
- Calls `cifs_sync_mid_result()` and dialect `check_receive()` for each response.
- Transfers response buffers to caller-owned `resp_iov` when requested.
- Deletes non-cancelled MIDs at exit.

`cifs_sync_mid_result()` maps MID states:
- `MID_RESPONSE_READY` succeeds.
- `MID_RETRY_NEEDED` maps to `-EAGAIN`.
- malformed response maps through an EIO trace.
- shutdown maps to `-EHOSTDOWN`.
- `MID_RC` returns the stored MID rc.
- unknown states are dequeued and treated as invalid.

## Channel Selection
`cifs_pick_channel()` selects an SMB multichannel transport:
- Walks `ses->chans` under `chan_lock`.
- Skips null, terminating, and reconnect-needed channels.
- Chooses the least-loaded eligible channel by `server->in_flight`.
- Uses a round-robin start index through `ses->chan_seq`.
- Falls back to primary channel if none else is eligible.

## Large Read Receive
`cifs_readv_receive()` handles READ response payload delivery into a netfs/CIFS I/O subrequest:
- Reads the rest of the READ response header into `server->smallbuf`.
- Detects session expiry and status-pending interim responses.
- Sets up an iov for signature/credit processing.
- Maps SMB status to Linux error.
- Validates that enough READ response header arrived.
- Validates data offset against the current read position and small buffer limit.
- Reads padding/junk before the data payload.
- Uses dialect read-data length helpers, with SMB Direct RDMA memory-registration handling when configured.
- Reads payload into `rdata->subreq.io_iter`.
- Discards any trailing data before dequeuing the MID.
- Marks malformed reads through EIO trace helpers.

## State And Synchronization
Important lock domains:
- `server->srv_mutex`/`cifs_server_lock()` serializes signing and socket send ordering.
- `server->req_lock` protects credits and `in_flight`.
- `server->mid_queue_lock` protects the pending MID queue and MID deletion state.
- `mid->mid_lock` protects wait cancellation callback changes.
- `ses->chan_lock` protects multichannel channel selection.
- `ses->ses_lock` protects session status checks for preauth hash updates.

## Error Handling
The file is defensive about:
- stale credits across reconnect instances.
- partial sends requiring reconnect.
- invalid MID states.
- compound send failures requiring MID rollback and credit return.
- interrupted waits and cancellation ownership.
- malformed READ responses, short headers, overlarge offsets, and length overflows.
- server exiting state before credit waits.

## Risks And Review Focus
- Credit accounting and reconnect instance checks are correctness-critical; leaking or double-returning credits can deadlock or overload sessions.
- MID ownership is subtle when waits are cancelled because demultiplex callbacks may release cancelled MIDs asynchronously.
- Compound response ownership depends on `resp_iov`, `resp_buf_type`, and `CIFS_NO_RSP_BUF`; mistakes can leak or double-free SMB buffers.
- Partial send handling must always reconnect, since a later SMB frame could otherwise be interpreted as the remainder of a broken frame.
- Read receive validation is security-sensitive because it consumes server-provided offsets and lengths.

## Research Takeaways
`transport.c` is the SMB client’s concurrency and flow-control core. It ties together credits, MIDs, reconnects, signing/encryption send serialization, compound response demultiplexing, cancellation, and large read payload delivery.
