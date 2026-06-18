# sources/storage-engines/rocksdb/table/block_based/mock_block_based_table.h

## Purpose
Provides minimal block-based table scaffolding for unit tests that need a `BlockBasedTable` and filter builder context without opening a real SST file.

## Important APIs, Types, And Functions
`mock::MockBlockBasedTable` publicly exposes a constructor around `BlockBasedTable::Rep`. `mock::MockBlockBasedTableTester` owns `Options`, `ImmutableOptions`, `EnvOptions`, `BlockBasedTableOptions`, `InternalKeyComparator`, and a `BlockBasedTable`. Constructors accept raw or shared `FilterPolicy`. `GetBuilder` creates a `FilterBuildingContext` and calls `BloomFilterPolicy::GetBuilderFromContext`.

## Control Flow
Tests instantiate the tester with a filter policy. The constructor stores the policy in table options, creates a `BlockBasedTable::Rep` with fixed file size and mock level, and wraps it in `MockBlockBasedTable`. `GetBuilder` populates context fields such as column family name, compaction style, level, and logger before asking the filter policy for a builder.

## State And Persistence Behavior
All state is in memory. No table file is opened or persisted. The mock `Rep` is enough for filter builders/readers that inspect table options and immutable options.

## Dependencies And Integration Points
Depends on public filter policy API, block-based table reader internals, and internal filter policy context. Used by `full_filter_block_test.cc` and similar tests.

## Risks And Edge Cases
The mock table is intentionally incomplete; tests using it must avoid code paths that require real file handles, block handles, or loaded table properties. The raw-pointer constructor wraps ownership into `std::shared_ptr<const FilterPolicy>`, so callers should not reuse/delete the pointer separately.

## Test Signals
Successful construction of full-filter readers/builders in tests without real SST files is the main signal.
