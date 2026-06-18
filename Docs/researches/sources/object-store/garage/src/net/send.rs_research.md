# sources/object-store/garage/src/net/send.rs

## Purpose
This file implements the sending half of the custom multiplexed stream protocol. It queues request/response streams by priority, chunks them into frames, honors optional order tags, sends cancellation frames, and writes encrypted transport bytes.

## Important APIs, types, and functions
Protocol constants define `RequestID`, `ChunkLength`, `MAX_CHUNK_LENGTH`, continuation/error flags, length mask, and `CANCEL_REQUEST`. `SendItem` is either a stream or cancellation. `SendQueue`, `SendQueuePriority`, and `SendQueueItem` implement scheduling. `DataFrame` encodes data or error chunks. `SendLoop::send_loop` drives channel receive and frame writes.

## Control flow
New streams are inserted into a priority-sorted queue, with lower priority values sent first. Within a priority, `poll_next_ready` first polls streams that have sent zero bytes so small requests can go out quickly, then all streams round-robin. Streams with `OrderTag`s wait until their order number is at the front for that tag stream. Each ready packet becomes a data frame with continuation flag based on stream EOS, or an error frame with encoded I/O kind/message. Cancellation removes queued work and writes a special cancel header. The loop exits after the input channel closes and queued streams drain, then sends transport goodbye.

## State and persistence behavior
All state is per connection and in memory. No persistence. The chunk format is the internal wire protocol consumed by `recv.rs`.

## Dependencies and integration points
It depends on `ByteStreamReader`, message priorities/order tags, error kind encoding, bytes buffers, futures polling, `kuska_handshake::BoxStreamWrite`, and tokio mpsc. `ClientConn` and server connections implement `SendLoop`.

## Risks and edge cases
Unbounded mpsc channels can grow if producers outpace the transport. Order-tag bookkeeping uses unwrap/assert paths and assumes remove/send completion paths remain consistent. Error messages are truncated to fit one chunk. Frequent `flush` after every frame favors latency over throughput. Cancellation only removes queued outgoing data; already transmitted data may still be processed remotely.

## Test signals
No direct unit tests. Useful tests should cover priority ordering, round-robin chunking, order tags, cancellation frames, error-frame truncation, queue removal, and interoperation with `recv_loop`.
