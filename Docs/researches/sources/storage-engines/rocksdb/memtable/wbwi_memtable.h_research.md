# sources/storage-engines/rocksdb/memtable/wbwi_memtable.h

## Purpose
`wbwi_memtable.h` declares `WBWIMemTable`, a `ReadOnlyMemTable` implementation backed by `WriteBatchWithIndex`, and `WBWIMemTableIterator`, which converts WBWI entries into internal-key iterator output with assigned sequence numbers.

## Important APIs, Types, and Functions
- `WBWIMemTable::SeqnoRange` stores lower and upper assigned sequence bounds.
- The constructor stores the shared WBWI, comparator, column family ID, immutable/mutable options, clock, and entry count including overwritten single deletes.
- `AssignSequenceNumbers()` sets the immutable sequence range exactly once.
- `NewIterator`, `Get`, and `MultiGet` implement the main read/flush interfaces.
- `WBWIMemTableIterator` implements `InternalIterator` over WBWI entries, including `Seek`, `SeekForPrev`, `Next`, `Prev`, `NextAndGetResult`, `key`, `value`, and `status`.

## Control Flow
WBWI entries do not contain sequence numbers, so `CurrentKeySeqno()` computes `lower_bound + update_count - 1`. `UpdateKey()` maps the WBWI write type to an internal `ValueType` and constructs an internal key. Flush iteration can emit overwritten `SingleDelete` records: when `for_flush` is true and the current WBWI entry reports an overwritten single delete, `Next()` first synthesizes a `kTypeSingleDeletion` at `lower_bound` before advancing the underlying iterator.

`Seek()` and `SeekForPrev()` translate an internal target to a user-key seek in WBWI, then step within equal user keys until the computed sequence number satisfies the internal target sequence constraint. Reverse and random access assert that overwritten-single-delete emission is not active because flush uses forward sequential iteration.

## State and Persistence Behavior
The memtable is read-only, references shared WBWI data, and tracks assigned sequence numbers plus minimum prepare-log reference. Many stats methods are placeholders returning zero or empty values. Persistence occurs when flush consumes the iterator and writes internal keys to SST files; this class only supplies the in-memory view.

## Dependencies and Integration Points
The header depends on `db/memtable.h` and `write_batch_with_index.h`. It integrates with transaction ingestion, read paths expecting `ReadOnlyMemTable`, flush job iteration, merge handling, and WAL retention through `GetMinLogContainingPrepSection`.

## Risks and Test Signals
The implementation requires WBWI overwrite mode. Unsupported areas are explicit: mempurge sampling, UDT timestamp stripping, range tombstones, newest UDT, and many size/stat estimates. Sequence assignment must happen before reads or iterator creation. The overwritten single-delete logic is subtle but important to prevent older values from incorrectly resurfacing after flush/compaction. Dedicated tests are not present in this subset.
