# sources/storage-engines/rocksdb/utilities/compaction_filters.cc

## Purpose
This file registers and loads RocksDB compaction filters from string configuration. It provides the built-in registration hook for `RemoveEmptyValueCompactionFilter`.

## Important APIs, Types, and Functions
`RegisterBuiltinCompactionFilters` adds a factory for `RemoveEmptyValueCompactionFilter::kClassName()` to the default `ObjectLibrary`. `CompactionFilter::CreateFromString` registers built-ins once with `std::call_once`, then calls `LoadStaticObject`. `CompactionFilterFactory::CreateFromString` delegates to `LoadSharedObject` and currently has no built-in factories to register.

## Control Flow
The first `CreateFromString` call initializes built-in filter factories. Then the requested string value is resolved through RocksDB's static object loader into a `CompactionFilter*`. Factory loading simply attempts shared/static configuration loading and returns the resulting status.

## State and Persistence Behavior
The only persistent state is the process-global registration in `ObjectLibrary::Default()` guarded by a static `once_flag`. Created filters are returned to callers according to RocksDB's customizable object conventions.

## Dependencies and Integration Points
This file depends on `rocksdb/compaction_filter.h`, options/customizable loading, and the remove-empty-value filter implementation. It is used by options parsing and configuration strings that name compaction filters.

## Risks and Edge Cases
Only a single built-in `CompactionFilter` is registered; built-in factories are explicitly absent. The code casts through `const_cast` because the public API returns a const filter pointer, so ownership and lifetime must follow the customizable loader contract. A missing or misspelled class name returns a loader error rather than a fallback.

## Test Signals
Useful tests parse `RemoveEmptyValueCompactionFilter` by class name, verify unknown filters fail, and ensure factory string loading still works for user-registered/shared filters.
