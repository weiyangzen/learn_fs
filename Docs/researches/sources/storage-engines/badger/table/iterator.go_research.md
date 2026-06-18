# sources/storage-engines/badger/table/iterator.go

## Purpose
This file implements SSTable block iteration, table iteration, and concatenated table iteration. It decodes the prefix-compressed block format produced by `builder.go`, navigates across table blocks, and exposes forward or reversed `y.Iterator` behavior.

## Important APIs, Types, and Functions
- `blockIterator` holds decoded block state: data, entry index, base key, current key/value, offsets, table/block IDs, and overlap cache.
- `setBlock`, `setIdx`, `seek`, `seekToFirst`, `seekToLast`, `next`, and `prev` implement in-block navigation.
- `Iterator` wraps a `Table` and a `blockIterator`, with `NewIterator`, `Close`, `Seek`, `Rewind`, `Next`, `Key`, `Value`, and `ValueCopy`.
- Constants `REVERSED` and `NOCACHE` configure direction and block-cache use.
- `ConcatIterator` lazily opens table iterators over non-overlapping tables and moves between them.

## Control Flow and State Behavior
`blockIterator.setIdx` reconstructs the current key by decoding the entry header, reusing previous overlap state to avoid unnecessary base-key copies, and slicing the encoded value bytes. Invalid indexes set `io.EOF`. A recovery block adds detailed table/block/index diagnostics if malformed block data panics during slicing.

`Iterator.seekFrom` binary-searches table block offsets for the block whose smallest key bounds the target, then seeks inside that block. If the target is beyond that block, it advances to the next block. Forward and reverse public methods dispatch to internal `next`/`prev` based on `REVERSED`. `Close` releases the current block and decrements the table reference.

`ConcatIterator` assumes its tables are ordered and non-overlapping. It increments table refs on construction, lazily constructs table iterators, seeks to the table whose range can contain the key, and advances table-by-table.

## Dependencies and Integration Points
The file depends on `Table.block`, FlatBuffer block offsets, builder's block header encoding, and `y.CompareKeys`/`ValueStruct`. It is used by Badger levels, compaction, reads, and merge iterators.

## Risks and Edge Cases
Correctness depends on block offset metadata, prefix-compression decode alignment, and table range ordering for concat iteration. `seekForPrev` performs a forward seek and then `prev`, with a TODO noting possible optimization. `Close` must be called to release table and block refs. `Iterator.Valid` reflects `itr.err == nil`; callers should not use `Key`/`Value` after invalidation.

## Test Signals
`table_test.go` exercises seek boundaries, forward/backward movement, full scans, reverse iteration, concat iteration over multiple tables, and large values.
