# sources/storage-engines/rocksdb/utilities/compaction_filters/remove_emptyvalue_compactionfilter.h

## Purpose
This header declares the built-in compaction filter that drops entries with empty values.

## Important APIs, Types, and Functions
`RemoveEmptyValueCompactionFilter` derives from `CompactionFilter`, exposes stable class name `RemoveEmptyValueCompactionFilter`, overrides `Name`, and declares `Filter`.

## Control Flow
The header defines the filter contract; implementation is the empty-value predicate in the `.cc` file.

## State and Persistence Behavior
The class has no data members and therefore no per-instance mutable state.

## Dependencies and Integration Points
It depends on RocksDB compaction filter and slice APIs. The class name is used by built-in object-library registration.

## Risks and Edge Cases
Changing `kClassName` breaks string-based option compatibility. Because the filter has no configuration, deployments needing conditional empty-value handling need a different filter.

## Test Signals
Compile/link coverage plus configuration-loading and compaction behavior tests provide the main confidence signals.
