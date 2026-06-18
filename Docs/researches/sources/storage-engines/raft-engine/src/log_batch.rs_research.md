# sources/storage-engines/raft-engine/src/log_batch.rs

## Purpose
`log_batch.rs` defines the logical and physical batch format for raft-engine log writes. It serializes raft entry indexes, commands, and key-value operations; stores entry bytes in a contiguous entries block; optionally compresses entry bytes; signs and verifies checksums; tracks post-write file handles; and embeds atomic group markers for persistent multi-batch rewrite atomicity.

## Important APIs, Types, And Functions
`MessageExt` abstracts over protobuf entry types so `LogBatch::add_entries` can obtain raft log indexes. `CompressionType` currently supports `None` and `Lz4`.

`EntryIndexes` encodes a count, first index, and tail offsets, reconstructing per-entry `EntryIndex` offsets and lengths during decode. `Command` supports `Clean` and `Compact { index }`. `OpType` supports `Put` and `Del`; `KeyValue` encodes operation type, key, and optional value plus an optional source `FileId`.

`LogItem` combines a raft group id with `LogItemContent` (`EntryIndexes`, `Command`, or `Kv`). `LogItemBatch` is the footer-only batch of logical items. It can merge batches, encode/decode item metadata, update entry compression type, sign footer checksum with a `LogFileContext`, and fill entry or key-value file locations after the physical write.

`LogBatch` is the full write unit. It owns a `LogItemBatch`, a state-machine enum `BufState`, and the encoded buffer. Public mutation methods include `merge`, `add_entries`, `add_command`, `delete`, `put_message`, `put`, `is_empty`, and `approximate_size`. Crate-internal persistence methods include `finish_populate`, `prepare_write`, `encoded_bytes`, `finish_write`, `drain`, `decode_header`, and `decode_entries_block`.

`verify_checksum_with_signature` validates a trailing CRC32, optionally XORing the expected checksum with a file-context signature. `AtomicGroupStatus` parses internal key markers. `AtomicGroupBuilder` writes begin, middle, and end markers using reserved internal keys.

## Control Flow
A normal write starts with an open `LogBatch` containing a 16-byte header placeholder. Callers add entries and metadata. Entry bytes are appended after the header while corresponding `EntryIndex` records are added to the item footer with offsets relative to the entries block. `finish_populate` optionally LZ4-compresses the entries block, appends an entries CRC, records the footer offset, encodes the `LogItemBatch`, writes the big-endian header `{u56 len | u8 compression type, u64 footer offset}`, and moves the buffer to `Encoded`.

`prepare_write` signs the footer checksum using the target `LogFileContext` and moves the batch to `Sealed`. `encoded_bytes` then exposes the exact slice to write. After the pipe returns a `FileBlockHandle`, `finish_write` adjusts it from full batch to entries-block coordinates and stores it into each entry index or key-value metadata. `drain` resets the buffer to the header placeholder and returns logical items for memtable application.

Decoding reverses this structure. `decode_header` validates the 16-byte header and returns footer offset, compression type, and total batch length. `LogItemBatch::decode` verifies the signed footer checksum, decodes item metadata, assigns entry handles and compression types, and records key-value file ids. `decode_entries_block` verifies the entries-block checksum and decompresses if needed.

## State And Persistence Behavior
`BufState` prevents invalid call ordering: `Open` accepts mutations, `Encoded` is populated but unsigned for a specific file, `Sealed` is ready to write, and `Incomplete` protects temporary mutation windows. Several methods use debug assertions or `unreachable!`, so violating the call protocol can panic.

The on-disk batch has a fixed 16-byte header, optional entries block plus CRC, and footer item batch plus CRC. For V2-style signed log files, footer checksums are XORed with the log file signature derived from file id and version, detecting batches moved to the wrong file. Entries-block checksums are not signed. Empty batches encode to length zero and carry no physical data.

The entries block is limited to `i32::MAX` bytes for LZ4 compatibility. User `put` and `put_message` reject reserved internal-key prefixes; atomic group markers bypass that via `put_unchecked`.

Atomic group markers are persisted as internal key-value items with an atomically assigned group id and status byte. Recovery can parse these markers and treat groups as persistent rewrite units, with caveats documented in the file: in-memory state may differ after failure until recovery, replay order is group-level rather than original write order, and older versions may expose markers as user keys.

## Dependencies And Integration Points
This file depends on varint and fixed-number codec helpers, protobuf `Message`, memtable `EntryIndex`, metrics `StopWatch`, `pipe_log` handles and contexts, CRC32 and LZ4 utilities, and crate-level internal-key helpers. `Engine` write paths build `LogBatch` values, `file_pipe_log::pipe` writes them through `ReactiveBytes`, `reader` and recovery decode them, `filter` rewrites them, and memtable/purge logic consumes the drained `LogItem`s and file handles.

## Risks And Edge Cases
`CompressionType::from_u8` and `OpType::from_u8` use `transmute` after range checks; this is compact but relies on enum discriminants remaining dense from zero or one as implemented. `KeyValue::decode` trusts encoded lengths enough to slice the input, so malformed short buffers can panic if codec length validation does not catch them first. Many call-order violations panic rather than returning errors. `AtomicGroupStatus::parse` unwraps status conversion and can panic on a malformed internal marker value. Repeated `prepare_write` intentionally re-signs the same populated batch for different file contexts; tests cover this, but callers must not mutate content afterward.

## Test Signals
Tests cover entry-index encoding, command encoding, key-value encoding including invalid op types and delete-with-value behavior, log-item encoding, `LogItemBatch` signing and decoding, full `LogBatch` encode/decode across versions and compression modes, merge offset adjustment, empty batches, internal-key rejection, header corruption, repeated signature signing, and a nightly encode benchmark. These tests also verify wrong file/version signatures fail under signed versions and that decoded entries match original raft protobuf entries.
