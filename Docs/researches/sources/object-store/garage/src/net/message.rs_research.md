# sources/object-store/garage/src/net/message.rs

## Purpose
This file defines the typed request/response model and wire encoding for endpoint messages, including priorities, optional attached byte streams, order tags, and request/response framing inside logical streams.

## Important APIs, types, and functions
`RequestPriority` plus constants `PRIO_HIGH`, `PRIO_NORMAL`, `PRIO_BACKGROUND`, `PRIO_PRIMARY`, and `PRIO_SECONDARY` drive send queue scheduling. `OrderTag`/`OrderTagStream` order related messages. `Message` defines associated response type. `Req<M>` and `Resp<M>` wrap serialized messages and optional `ByteStream`s with builder/accessor methods. `IntoReq` converts messages or existing requests. `AttachedStream` converts fixed bytes or streams into `ByteStream`. `ReqEnc` and `RespEnc` encode/decode path, telemetry ID, message bytes, and attached streams.

## Control flow
Requests serialize messages using named rmp-serde. `ReqEnc::encode` writes priority, path length/path, telemetry length/ID, message length/message, then chains any attached stream. `ReqEnc::decode` reads those fields and exposes the remaining stream. Responses encode a u32 message length/message and optional stream; response errors become a stream yielding an I/O error. `RespEnc::decode` reads the response message and calls `fill_buffer` to detect EOS early, avoiding unnecessary cancellation when the caller ignores an empty stream.

## State and persistence behavior
No persistent state. The byte layout is the internal `garage_net` wire contract between compatible peers. `OrderTag` carries random stream IDs and order numbers only in memory/wire frames.

## Dependencies and integration points
It depends on `bytes`, `rand`, `serde`, `rmp-serde`, futures streams, byte stream utilities, and network errors. Endpoints, client/server connections, and send loops use these structures.

## Risks and edge cases
Path and telemetry lengths are encoded as `u8`, so paths/telemetry IDs above 255 bytes truncate by cast during encode; endpoint paths should remain short. `Req::clone` panics for non-buffer streams. Error responses are encoded as stream errors rather than structured typed response errors. Local endpoint calls may skip serialization and miss encode failures.

## Test signals
No direct tests in this file. Network tests should cover request/response round trips, attached streams, error streams, priority propagation, order tags, clone behavior, path length limits, and empty-stream cancellation defusing.
