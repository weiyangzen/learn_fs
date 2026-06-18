# sources/storage-engines/rocksdb/include/rocksdb/utilities/debug.h

## Purpose
Public diagnostic API for listing all internal versions of keys in a user-key range.

## Important APIs, Types, And Functions
`KeyVersion` stores `user_key`, `value`, `sequence`, and integer `type`, with `GetTypeName()` for readable output. `GetAllKeyVersions` has default-CF and explicit-CF overloads and accepts inclusive begin/end keys plus `max_num_ikeys`.

## Control Flow, State, And Persistence
The implementation scans internal versions and appends copied `KeyVersion` records until the inclusive range ends or the maximum internal-key count is reached. It is read-only and materializes results in caller memory.

## Dependencies And Integration Points
Depends on `DB`, `ColumnFamilyHandle`, `OptSlice`, and `SequenceNumber`. It integrates with internal versioned-key iteration and debugging tools.

## Risks And Edge Cases
Large ranges can consume substantial memory because keys and values are copied. The range is inclusive-inclusive, unlike many half-open RocksDB APIs. Tombstones, merges, and old snapshot-hidden versions may appear.

## Test Signals
Check sequence/type reporting, inclusive end handling, max-count truncation, CF overload behavior, tombstones/merges, and empty ranges.
