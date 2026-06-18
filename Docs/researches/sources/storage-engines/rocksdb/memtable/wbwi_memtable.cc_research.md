# sources/storage-engines/rocksdb/memtable/wbwi_memtable.cc

## Purpose
`wbwi_memtable.cc` implements the executable behavior of `WBWIMemTable`, a read-only memtable view over `WriteBatchWithIndex` content used when ingesting a transaction-like batch as an immutable memtable.

## Important APIs and Functions
- `WBWIMemTableIterator::WriteTypeToValueTypeMap` maps WBWI write record types to RocksDB internal value types.
- `WBWIMemTable::NewIterator(...)` constructs an arena-allocated `WBWIMemTableIterator` for flush or read paths.
- The private `NewIterator() const` creates a heap iterator for point lookups.
- `Get()` implements read lookup, merge handling, deletion handling, visibility callback checks, and unsupported type detection.
- `MultiGet()` loops over a `MultiGetRange` and delegates to `Get()` per key.

## Control Flow
Iterator creation asserts sequence numbers have been assigned and obtains a WBWI column-family iterator for `cf_id_`. `Get()` seeks the internal lookup key, then walks entries with the same user key. For visible entries, it records the output sequence, applies covering tombstone logic, and dispatches by value type: value returns through `HandleTypeValue`, deletions through `HandleTypeDeletion`, merge operands through `HandleTypeMerge`, and unsupported types produce corruption. If iteration ends while merge operands are accumulated, it returns `MergeInProgress`.

`MultiGet()` performs a straightforward per-key loop. When a final value is found, it pins the result, updates aggregate value size, marks the key done, and aborts remaining keys if the soft value-size limit is exceeded.

## State and Persistence Behavior
The class reads from an existing `WriteBatchWithIndex`; it does not mutate it. The assigned sequence range determines internal key ordering. It assumes the memtable is immutable and that no snapshot sequence lies inside the assigned sequence range.

## Dependencies and Integration Points
The implementation depends on `memtable/wbwi_memtable.h` and `db/memtable.h` helper routines for value, deletion, and merge handling. It integrates with transaction ingestion, flush iteration, and read-only memtable lookup paths.

## Risks and Test Signals
Several features are intentionally unsupported or asserted away: user-defined timestamps, blob index resolution, delete range, wide-column entity reads, and value preferred seqno. `MultiGet()` is functionally correct but not optimized because it creates point lookup iterators through `Get()`. No dedicated test is in this subset; correctness depends on WBWI/transaction ingestion tests elsewhere.
