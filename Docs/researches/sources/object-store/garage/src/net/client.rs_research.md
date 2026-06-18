# sources/object-store/garage/src/net/client.rs

## Purpose
This file implements outgoing client-side NetApp connections. It authenticates to peers, checks protocol/app version tags, starts send/receive loops, tracks in-flight requests, and cancels remote streams when callers drop responses early.

## Important APIs, types, and functions
`ClientConn` stores remote address, peer ID, optional send channel, atomic next request ID, and `inflight` response waiters. `ClientConn::init` performs handshake and loop setup. `close` drops the send channel. `call` encodes a request, registers a oneshot response channel, sends a stream item, waits for and decodes the response. `CancelOnDrop` and `CancelOnDropStream` send cancel frames unless response streams reach EOS.

## Control flow
Initialization performs `kuska_handshake` client auth using network and node keys, wraps the socket in encrypted `BoxStream`, reads the remote version tag, and rejects mismatches. It then registers the connection, spawns send and recv loops, clears in-flight requests on shutdown, and deregisters from `NetApp`. `call` allocates a u32 request ID, optionally starts telemetry, encodes the request path/message/stream, inserts the inflight waiter, sends `SendItem::Stream`, wraps the response stream with cancellation-on-drop, decodes `RespEnc`, and deserializes the typed response.

## State and persistence behavior
All state is transient per TCP connection. In-flight request IDs wrap at u32 and collisions are detected by replacing and erroring the old request. Dropping `query_send` closes the connection.

## Dependencies and integration points
It depends on `NetApp`, endpoint/message encoding, send/recv loops, byte streams, tokio channels, futures, `kuska_handshake`, sodium keys through `NetApp`, and optional OpenTelemetry. `Endpoint::call_streaming` delegates remote calls to `ClientConn::call`.

## Risks and edge cases
The comment notes send-loop shutdown should wait for in-flight responses; currently send loop completion stops recv loop and clears inflight. Request ID collision is possible after wraparound under very long-lived high-volume connections. Cancellation is suppressed only when the response stream returns `None`; callers that do not drain attached streams will cancel server work. Version mismatch aborts connection before request handling.

## Test signals
No direct unit tests in this file; crate-level network tests exercise calls. Useful tests should cover version mismatch, request cancellation, stream-drop cancellation, in-flight clearing on disconnect, telemetry feature builds, and request ID collision behavior.
