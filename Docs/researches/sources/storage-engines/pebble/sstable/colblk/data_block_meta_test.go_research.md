<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/data_block_meta_test.go -->
# sources/storage-engines/pebble/sstable/colblk/data_block_meta_test.go

## Purpose
`data_block_meta_test.go` verifies that columnar data-block iterators correctly return per-KV tiering metadata through the meta iterator methods. It focuses on optional tiering columns introduced through `OptionalColumnConfig`.

## Important APIs, Types, And Functions
The key test is `TestDataBlockIterWithMeta`. It uses `WithTieringColumns`, `DataBlockEncoder.Add`, `DataBlockIter.FirstWithMeta`, `NextWithMeta`, and `SeekGEWithMeta`.

## Control Flow
The test builds a default-schema data block with three keys and explicit `base.KVMeta` values, including a zero-valued metadata row. It finishes and decodes the block, initializes a `DataBlockIter` with tiering enabled, walks all rows through `FirstWithMeta` and `NextWithMeta`, checks exhaustion returns nil plus empty metadata, and tests `SeekGEWithMeta` for both present and absent targets.

## State And Persistence Behavior
The test exercises persisted tiering span ID and tiering attribute columns. It also covers lazy metadata decoding in `DataBlockIter`: tiering columns are decoded only when `decodeMeta` is needed, not during ordinary key/value iteration.

## Dependencies And Integration Points
It integrates `DefaultKeySchema`, `testkeys.Comparer`, `block.InPlaceValuePrefix`, `blockiter.Transforms`, and `testify/require`. The tested API is part of `base.MetaIterator` behavior used by consumers that need tiering metadata during iteration.

## Risks
Coverage is intentionally narrow: it does not test `InitHandle`, secondary blob handle persistence, transforms combined with metadata, or mismatched optional column configs. A nil lazy value handler is safe here because all values are in-place.

## Test Signals
The test directly guards the `DataBlockIter` `FirstWithMeta`, `NextWithMeta`, and `SeekGEWithMeta` paths and validates empty metadata on iterator exhaustion or missing seek results.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/sstable/colblk/data_block_meta_test.go -->
