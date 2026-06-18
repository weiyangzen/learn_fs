# sources/storage-engines/rocksdb/utilities/debug.cc

## Purpose
This file implements debug utilities for inspecting internal key versions in a RocksDB DB or column family.

## Important APIs, Types, and Functions
`value_type_string_map` maps internal `ValueType` enum names to enum values. `KeyVersion::GetTypeName` serializes the numeric type back to a string or returns `Invalid`. `GetAllKeyVersions` has overloads for the default column family and an explicit `ColumnFamilyHandle`.

## Control Flow
The public overload validates the DB pointer and delegates to the CF-aware overload. The CF-aware overload validates DB, CF handle, and output vector; clears the output; obtains the root `DBImpl`; creates an `InternalKeyComparator`; opens a new internal iterator at `kMaxSequenceNumber`; adjusts optional begin/end bounds for timestamped comparators; seeks to the beginning bound or first key; then iterates internal entries until invalid, past end bound, parse failure, or `max_num_ikeys` is reached.

## State and Persistence Behavior
The function is read-only against the DB but exposes internal key/value versions into a caller-owned vector. Returned keys and values are copied to strings. It uses current internal iterator state, not a user snapshot.

## Dependencies and Integration Points
It depends on `DBImpl`, internal key parsing/comparison, timestamp range helpers, `Arena`, `ScopedArenaPtr`, `ReadOptions`, and RocksDB's options enum serialization utilities. It powers public debug APIs in `rocksdb/utilities/debug.h`.

## Risks and Edge Cases
This code reaches into `DBImpl` internals and assumes the DB pointer can be cast to the expected implementation via `GetRootDB`. It returns internal records, including deletions, merges, range deletions, blob indexes, wide-column entities, transaction markers, and timestamp variants, so callers must not treat output as normal user-level state. Range end comparison uses `> 0`, so equality with the end key remains included. Parse errors abort the scan.

## Test Signals
Tests should insert puts/deletes/merges across sequence numbers, call `GetAllKeyVersions` with and without bounds, verify type names, timestamped comparator ranges, column-family handling, null-argument validation, and `max_num_ikeys` limiting.
