# sources/storage-engines/rocksdb/utilities/compaction_filters/remove_emptyvalue_compactionfilter.cc

## Purpose
This file implements a simple compaction filter that removes key-value entries whose existing value is empty.

## Important APIs, Types, and Functions
`RemoveEmptyValueCompactionFilter::Filter` overrides `CompactionFilter::Filter`. It ignores level, key, output value, and value-changed parameters, and returns `existing_value.empty()`.

## Control Flow
Every compaction-filter callback is a single predicate check. Empty values return true, instructing RocksDB to drop the key; non-empty values return false and are kept unchanged.

## State and Persistence Behavior
The filter is stateless. Its persistent effect occurs during compaction: keys with empty values are omitted from newly written SST files.

## Dependencies and Integration Points
It depends on `rocksdb::Slice` and is registered as a built-in string-loadable compaction filter in `utilities/compaction_filters.cc`.

## Risks and Edge Cases
This filter treats an empty value as deletion-like during compaction, which is safe only for workloads where empty values are not meaningful. It does not set `value_changed` or rewrite values. It does not inspect merge operands before they are resolved.

## Test Signals
Tests should verify that empty values disappear after compaction, non-empty values remain, and the filter can be created by the registered class name.
