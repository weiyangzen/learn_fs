# sources/storage-engines/pebble/sstable/rowblk/rowblk_writer_test.go

## Purpose
Provides focused unit coverage for the low-level row-block writer's state reset and exact byte encoding.

## Important APIs, Types, And Functions
`TestBlockWriterClear` exercises `Writer.Reset`. `TestBlockWriter` checks exact raw block output for `apple`, `apricot`, and `banana`. `TestBlockWriterWithPrefix` drives `AddWithOptionalValuePrefix` and inspects current key/value accessors and restart high-bit behavior.

## Control Flow And State
The tests write small blocks, compare internal writer state before and after reset, and compare the full encoded block bytes against hard-coded expected encodings. The prefix test uses restart interval 2 to produce multiple restart points and verifies that cumulative `setHasSameKeyPrefix` metadata is only set when all entries since the last restart kept the same prefix.

## Persistence And Integration
All persistence is in-memory encoded row blocks. The test protects the wire format consumed by `rowblk.Iter`, `RawIter`, table indexes, and properties blocks.

## Risks
Hard-coded bytes are precise and valuable but cover only small examples. They do not test `ErrBlockTooBig`, invalid restart intervals, high cardinality restart tables, or non-SET key kinds with obsolete bits.

## Test Signals
The file gives strong regression signal for byte-level compatibility of row-block encoding, especially value-prefix storage and restart high-bit encoding introduced for prefix skipping.
