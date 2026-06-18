# sources/storage-engines/badger/stream_test.go

## Purpose
This file tests the `Stream` export framework over managed Badger databases. It validates range streaming, prefix filtering, key selection, thread-id exposure, manual large-dataset behavior, and custom key-to-list callback ownership.

## Important Tests and Helpers
- `keyWithPrefix`, `keyToInt`, and `value` create predictable key/value fixtures.
- `collector.Send` decodes stream buffers with `BufferToKVList`, clones KVs, and ignores stream done markers.
- `TestStream` writes three prefixes at a managed timestamp and checks full export, prefix export, even-key selection within a prefix, and even-key selection across all prefixes.
- `TestStreamMaxSize` and `TestBigStream` are manual large tests that temporarily reduce `maxStreamSize` and stream millions of keys.
- `TestStreamWithThreadId` verifies each iterator's `ThreadId` is below `NumGo`.
- `TestStreamCustomKeyToList` checks a prior allocator double-free bug path by returning a custom list that copies item key/value data.

## Control Flow and State Behavior
Tests use `OpenManaged`, create transactions at `math.MaxUint64`, commit at timestamp 5, and stream at `math.MaxUint64` to include all data. The collector accumulates decoded protobuf KVs, then assertions count keys per prefix and verify values. `ChooseKey` is reassigned between orchestrations, demonstrating that a stream object can be reused serially after resetting relevant fields.

## Dependencies and Integration Points
The tests use `badger.Stream`, managed transactions, `pb.KV`, `z.Buffer`, protobuf cloning, and Badger item value APIs. They rely on `ctxb = context.Background()` and on test helpers such as `removeDir`.

## Risks and Edge Cases
The manual tests are skipped unless a manual flag is set, so routine test runs do not cover very large streams or soft max-size behavior. `collector.Send` ignores done markers, which is appropriate for these assertions but not a full restore protocol validation. The custom callback test intentionally returns only one version per key, so it validates callback ownership more than default version enumeration.

## Test Signals
The file gives strong evidence that `Stream.Orchestrate` respects prefix and `ChooseKey`, preserves values, supports thread IDs, and tolerates custom `KeyToList` without allocator lifetime regressions.
