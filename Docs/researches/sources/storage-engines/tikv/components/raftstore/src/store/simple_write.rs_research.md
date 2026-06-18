# sources/storage-engines/tikv/components/raftstore/src/store/simple_write.rs

## Purpose
`simple_write.rs` implements a compact binary encoding for simple raft write commands. It avoids full `RaftCmdRequest` protobuf overhead for common put/delete/delete-range/ingest operations, supports batching compatible operations with the same header, and can decode back into normal raft command requests when needed.

## Important APIs, Types, and Functions
`SimpleWriteEncoder` builds a `SimpleWriteBinary` by appending `put`, `delete`, `delete_range`, or `ingest` operations. `SimpleWriteBinary` owns the encoded operation bytes and records a private `WriteType`; `freeze` marks it unbatchable and `data_size` reports encoded size. `SimpleWriteReqEncoder<C>` wraps a raft request header, a magic-prefixed buffer containing length-delimited header plus simple-write operations, response channels, a size limit, and a write type. Its main APIs are `new`, `amend`, `encode`, `add_response_channel`, `data_size`, and `header`.

Operation structs are `Put`, `Delete`, `DeleteRange`, and enum `SimpleWrite<'a>`, with `Ingest(Vec<SstMeta>)` for SST ingestion. `SimpleWriteReqDecoder<'a>` parses request buffers. `new` detects `MAGIC_PREFIX`; if absent it returns a fallback-decoded `RaftCmdRequest`. It implements `Iterator<Item = SimpleWrite<'a>>` and can materialize a full protobuf request via `to_raft_cmd_request`.

Private codec helpers include `encode_len`/`decode_len`, `encode_bytes`/`decode_bytes`, `encode_cf`/`decode_cf`, `encode`, and `decode`. CF names use one-byte tags for default/write/lock and an arbitrary string tag for other CFs. Operation tags distinguish put, delete, delete range, and ingest.

## Control Flow
Encoding starts with operation-level `SimpleWriteEncoder`. Each mutating method debug-asserts that operations are compatible with the existing write type: put/delete can mix, delete-range batches only with delete-range, and ingest batches only with ingest. `encode` freezes the current buffer into `SimpleWriteBinary`.

`SimpleWriteReqEncoder::new` creates the raft-log payload by writing `MAGIC_PREFIX`, serializing the header as a length-delimited protobuf, and appending the operation bytes. `amend` batches another binary only if headers are identical, write types match, the incoming type is not `Unspecified`, and the size limit would not be exceeded. Response callbacks are tracked separately in `channels` and returned with encoded bytes.

Decoding first checks the magic byte. Non-magic data is delegated to a caller-supplied fallback parser for normal protobuf raft commands. Magic data reads the length-delimited header and leaves the remaining operation bytes for iteration. The iterator repeatedly calls `decode`, which slices borrowed keys/values from the input for put/delete/delete-range and reads length-delimited `SstMeta` protobuf messages for ingest. `to_raft_cmd_request` converts each decoded simple operation into its equivalent protobuf `Request`.

The variable-length length codec uses a SQLite4-inspired scheme optimized for short keys/values: one byte up to 240, two bytes through 2287, three through 67823, then tagged big-endian three- or four-byte forms for larger values.

## State and Persistence Behavior
The module does not persist directly; its encoded buffers become raft log entry data elsewhere. Compatibility hinges on `MAGIC_PREFIX == 0x00`, chosen because protobuf field tags cannot start with zero. Old/non-simple log entries remain decodable through fallback. Corrupted magic-prefixed data panics or `slog_panic!`s while reading the header, and lower-level decode helpers also panic on malformed internal buffers.

## Dependencies and Integration Points
Dependencies include engine CF constants, kvproto raft command and SST metadata messages, protobuf coded streams, slog logging, and store callback traits. The codec integrates with raft proposal batching and apply-side command decoding. `peer_storage.rs` persists raft entries that may contain these compact buffers, while apply logic can use `SimpleWriteReqDecoder` to process them or convert back to protobuf requests.

## Risks and Edge Cases
The decoder assumes trusted raft log data after magic detection; truncated lengths, invalid CF tags, invalid UTF-8 arbitrary CFs, and invalid operation tags panic. Batching relies on `WriteType`; an empty encoder has `Unspecified`, and `freeze` prevents later coalescing. `amend` uses a strict `< size_limit` check, so exactly equal size is rejected. Ingest uses protobuf per SST for simplicity, so it does not share the zero-copy behavior of key/value operations.

## Test Signals
Tests validate put/delete/delete-range/ingest round trips, arbitrary CF names, header preservation, variable-length number boundaries, fallback decoding of normal protobuf `RaftCmdRequest`, rejection of mismatched headers/frozen binaries/oversized batches, and conversion back to full `RaftCmdRequest` for each operation type.
