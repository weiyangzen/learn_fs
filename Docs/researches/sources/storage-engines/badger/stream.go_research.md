# sources/storage-engines/badger/stream.go

## Purpose
This file implements Badger's `Stream` framework: a concurrent, snapshot-based scanner that partitions the keyspace into ranges, converts keys into protobuf KV lists, batches them into buffers, and serially calls a user-supplied `Send` callback. It is intended for backups, replication, and fast export/import workflows.

## Important APIs, Types, and Functions
- `Stream` exposes `Prefix`, `NumGo`, `LogPrefix`, `ChooseKey`, `KeyToList`, thread-id aware callbacks, `Send`, `SinceTs`, and soft `MaxSize`.
- `SendDoneMarkers` enables per-stream completion markers.
- `ToList` is the default highest-key-to-all-valid-versions conversion.
- `produceRanges` asks the DB for range splits and feeds them largest-first.
- `produceKVs` owns per-worker transactions, iterators, allocators, stream IDs, and per-range conversion.
- `streamKVs` serially drains producer buffers, slurps additional buffers up to `MaxSize`, logs rates, and calls `Send`.
- `Orchestrate` wires goroutines, cancellation, channels, defaults, and error propagation.
- `BufferToKVList` and `KVToBuffer` convert between protobuf KVs and `z.Buffer` slice records.

## Control Flow and State Behavior
`Orchestrate` creates a cancellable context, a range channel, and a bounded KV buffer channel. One goroutine produces key ranges. `NumGo` producer goroutines open read-only transactions at `readTs` when managed or a normal snapshot otherwise. Each range iterator scans all versions with optional prefix and `SinceTs`, skips duplicate logical keys by tracking `prevKey`, applies `ChooseKey` only to the highest version, and calls either `KeyToList` or `KeyToListWithThreadId`. Returned KVs receive a per-range `StreamId` and are encoded into `z.Buffer` batches.

The sender goroutine is deliberately single-threaded. It releases every buffer after send, tracks ETA/rate logging, and merges immediately available producer buffers into larger send batches until `MaxSize` is exceeded. Context cancellation stops producers if sending fails.

## Dependencies and Integration Points
The code depends on Badger `DB`, `Txn`, `Iterator`, protobuf package `pb`, `y` utilities, `z.Buffer` and `z.Allocator`, and `humanize` for logs. It integrates directly with `StreamWriter`: KVs include `StreamId` and optional `StreamDone` markers that the writer uses to demultiplex sorted streams.

## Risks and Edge Cases
`Send` is serial, but `ChooseKey` and key-to-list callbacks are concurrent and must be thread-safe unless the thread-id API is used. Custom `KeyToList` must stop on the first mismatching key or it can consume keys owned by the stream framework. The batch limit is soft: a single oversized list can exceed `MaxSize`. Buffer and allocator lifetimes are owned by the framework; retaining returned slices outside `Send` requires copying.

## Test Signals
`stream_test.go` verifies full and prefix scans, `ChooseKey`, thread-id propagation, manual large streams and max-size behavior, and a custom `KeyToList` regression around allocator ownership.
