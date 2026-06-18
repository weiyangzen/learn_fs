# sources/storage-engines/tikv/components/backup-stream/src/utils.rs

## Purpose
This file is the shared utility layer for TiKV backup-stream. It collects key encoding helpers, CF name normalization, backup metadata filename parsing, non-overlapping range indexing, raft command extraction, scheduler/error macros, backup-stream statistics recording, lock-filtering policy, async task waiting, read-throughput measurement, range predicates, sequential async file reading, compression writer dispatch, and redacted debug/log formatting for regions and key ranges.

## Important APIs, Types, And Functions
`wrap_key` converts raw user keys to MVCC encoded data keys with `txn_types::Key`. `cf_name` maps user/protobuf CF strings to `engine_traits` CF constants and reports invalid names as `ERR_CF`. `ParsedBackupMetaFileName` and `parse_backupmeta_filename` parse backupmeta file stems into `flush_ts`, `store_id`, min/max timestamp tags, and optional flags; the parser accepts reordered tags and rejects malformed ASCII/hex/tag layouts.

`SegmentMap<K,V>` stores non-overlapping half-open ranges in a `BTreeMap` keyed by range start. It supports insertion with overlap rejection, point lookup, interval lookup, and overlap detection. `request_to_triple` extracts put/delete raft command payloads into `(key,value,cf)`. `try_send!`, `debug!`, and `future!` are convenience macros for scheduler reporting, feature-gated debug logging, and opaque future signatures.

`FutureWaitGroup` tracks spawned async work via RAII `Work` handles and wakes all waiters when the running count returns to zero. `with_record_read_throughput` records read bytes using Linux thread IO stats when available, falling back to RocksDB `ReadPerfInstant`. `FilesReader` implements `AsyncRead` over a list of readers. `CompressionWriter`, `NoneCompressionWriter`, `ZstdCompressionWriter`, and `compression_writer_dispatcher` abstract local temp-file writing for uncompressed and zstd data. `debug_key_range`, `slog_region`, `debug_region`, and `debug_iter` centralize redacted diagnostics.

## Control Flow
Most helpers are leaf utilities, but several define small protocols. `parse_backupmeta_filename` validates the prefix, walks fixed-width tagged suffix chunks, stores tags in a `BTreeMap`, then requires the min-begin/min/max tags before returning a parsed struct. `SegmentMap::insert` rejects overlapping ranges before mutating the map; overlap checks first test whether the query start lies inside a prior range, then check the last range starting before the query end. `FutureWaitGroup::wait` uses a fast path for zero running work, registers a waker under a mutex, then rechecks the counter to avoid lost wakeups. `FilesReader::poll_read` advances to the next file only when the current reader produces no bytes.

## State And Persistence Behavior
The file has no durable state of its own. It defines in-memory state containers (`SlotMap`, `SegmentMap`, `FutureWaitGroup`) and local filesystem writers. `NoneCompressionWriter::done` flushes and calls `sync_all`; `ZstdCompressionWriter::done` shuts down the encoder and flushes the underlying buffer, relying on encoder shutdown for compressed stream finalization. Backupmeta parsing is pure but constrains persisted metadata naming consumed by later flush/checkpoint code.

## Dependencies And Integration Points
The module integrates with `engine_traits` CF names, RocksDB read performance counters, `tikv_util` logging/worker scheduling, `kvproto` backup/raft/region messages, `txn_types` key/lock types, `async_compression`, Tokio async IO, and backup-stream local modules (`Task`, `errors`, `router::TaskSelector`, metrics). The metrics helper records `CfStatistics` into `INITIAL_SCAN_STAT`; `handle_on_event_result` sends fatal backup-stream tasks through the scheduler when event recording fails.

## Risks And Edge Cases
The segment map assumes half-open ranges and disallows overlaps; callers needing overlapping intervals must not use it as a general segment tree. Empty end keys are treated as infinity in simple byte-range helpers, so callers must maintain the same convention. `FutureWaitGroup` can accumulate duplicate wakers if polled repeatedly before completion. Zstd `done` does not explicitly call `sync_all` on the file, unlike the uncompressed writer. `cf_name` reports unknown CFs but returns a sentinel string, so downstream code must ignore or reject `ERR_CF`.

## Test Signals
Inline tests cover redacted region/range formatting, range inclusion, backupmeta parser tag order and flags, malformed tag rejection, segment overlap behavior, heavy wait-group race patterns, read-throughput measurement, sequential `FilesReader`, and zstd/uncompressed compression writer round trips.
