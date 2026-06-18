# sources/object-store/garage/src/net/recv.rs

## Purpose
This file implements the receiving half of the custom multiplexed stream protocol. It reads chunk frames from a connection, reconstructs per-request byte streams, dispatches new streams to connection-specific handlers, and handles cancellation/error frames.

## Important APIs, types, and functions
`Sender` wraps an unbounded packet sender and sends a broken-pipe error on drop if the stream ended unexpectedly. `RecvLoop` defines `recv_handler`, optional `cancel_handler`, and async `recv_loop`.

## Control flow
`recv_loop` repeatedly reads request ID and chunk size/flags. A `CANCEL_REQUEST` frame removes any active stream, sends a cancel error into it, calls `cancel_handler`, and continues. Normal frames parse continuation/error flags, read the payload, create a new channel and call `recv_handler` for first chunks, forward data/error packets to the stream sender, and either keep the sender in the active map for continuations or close it at EOS.

## State and persistence behavior
State is transient per connection: a `HashMap<RequestID, Sender>` for streams in progress. No persistence.

## Dependencies and integration points
It depends on `send.rs` constants, `ByteStream`, error helpers for remote I/O errors, futures/Tokio async read, and mpsc streams. `ClientConn` and server connections implement `RecvLoop`.

## Risks and edge cases
The code indexes `next_slice[0]` for error frames, so malformed zero-length error frames would panic. It asserts no continuation on error frames. If the receiver side drops before EOS, `Sender` still consumes frames but signals broken pipe. Unexpected EOF cleanly exits the loop; other read errors abort connection.

## Test signals
No direct tests. Useful tests should cover multi-chunk stream reconstruction, cancellation, remote error frames, malformed frame handling, dropped receiver behavior, and concurrent stream IDs.
