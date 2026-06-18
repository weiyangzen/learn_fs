# sources/sync-backup/syncthing/lib/protocol/protocol.go

## Purpose
Core BEP connection implementation. It defines Syncthing protocol limits, public model/connection interfaces, the raw asynchronous connection, message framing/compression, request/response tracking, initial cluster-config gating, close semantics, keepalive timeouts, and protocol consistency checks.

## Important APIs, Types, and Functions
Public interfaces are `Model`, `RequestResponse`, `Connection`, and `ConnectionInfo`. `NewConnection` composes wrappers for model connection injection, native path conversion, encryption, raw transport, and wire-format conversion. `rawConnection` owns reader/writer counters, pending request map, inbox/outbox/close/cluster-config channels, closed state, and goroutine lifecycle. Key methods include `Start`, `Index`, `IndexUpdate`, `Request`, `ClusterConfig`, `DownloadProgress`, `readerLoop`, `dispatcherLoop`, `readMessage`, `writeMessage`, `writeCompressedMessage`, `Close`, `internalClose`, `pingSender`, `pingReceiver`, and `Statistics`. Validation helpers include `checkIndexConsistency`, `checkFileInfoConsistency`, `checkFilename`, `typeOf`, `newMessage`, and LZ4 helpers.

## Control Flow
`Start` launches reader, dispatcher, writer, ping sender, and ping receiver goroutines once. The writer loop requires a cluster config or close before sending ordinary outbox messages, enforcing the initial BEP handshake. The reader loop reads framed protobuf messages and skips unknown message types for forward compatibility. The dispatcher requires `ClusterConfig` before other message types, validates index and request invariants, delegates model callbacks, starts request handlers asynchronously, and routes responses to waiting request channels. Outgoing requests allocate an integer ID under `awaitingMut`, send the request, then wait for a response or context cancellation. Close first tries to send a BEP close message with timeout, then closes the underlying transport and notifies the model.

## State and Persistence Behavior
State is in-memory connection state: pending request channels, byte counters, start time, close channels, metrics, and goroutines. No durable data is written. The raw connection mutates outbound message structs by converting them to wire/encrypted forms in wrapper layers and mutates received values through native/encryption conversion. `internalClose` closes the underlying `io.Closer`, closes all awaiting request channels, waits for dispatcher shutdown when started, and calls `model.Closed` outside the start/stop lock.

## Dependencies and Integration Points
Depends on protobuf BEP types from `internal/gen/bep`, `protoutil`, LZ4, counting reader/writer and buffer pool code in the protocol package, encryption/wire-format/native model wrappers, connection metrics, and higher-level model implementations. Constants such as `MaxRequestSize`, block-size bounds, and `DesiredPerFileBlocks` are shared with scanner and file-info code.

## Risks and Edge Cases
Concurrency is the main risk: close can race with dispatcher callbacks, blocked writes, request waits, and ping timeouts. Request IDs are unbounded integers during a connection. Context cancellation on a request does not remove its awaiting channel until a response or connection close arrives. Message-length and decompressed-size checks are essential for memory safety. Filename and file-info consistency checks protect remote input, but they must stay aligned with scanner-generated valid `FileInfo` values. LZ4 decompression returns buffer-pool slices that must not leak incorrectly.

## Test Signals
`protocol_test.go` covers ping, close races, blocking sends, close timeout, cluster-config ordering, legacy protobuf compatibility, LZ4 round trips and compatibility bytes, filename validation, file-info consistency, block size thresholds, cluster config after close, dispatcher-to-close deadlock, request size limits, zero-size request acceptance, invalid request filename rejection, and index ID formatting.
