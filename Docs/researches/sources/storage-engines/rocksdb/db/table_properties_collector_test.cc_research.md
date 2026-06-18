# sources/storage-engines/rocksdb/db/table_properties_collector_test.cc

## Purpose

`table_properties_collector_test.cc` verifies user and internal table property collectors across block-based and plain table formats, including backward-compatible collector APIs and internal key statistic collectors.

## Important APIs, Types, and Functions

The test defines `TablePropertiesTest`, `MakeBuilder`, `RegularKeysStartWithA`, `RegularKeysStartWithABackwardCompatible`, `RegularKeysStartWithAInternal`, `RegularKeysStartWithAFactory`, `FlushBlockEveryThreePolicy`, `TestCustomizedTablePropertiesCollector`, and `TestInternalKeyPropertiesCollector`. It uses `GetDeletedKeys`, `GetMergeOperands`, `ReadTableProperties`, and table builders over in-memory `StringSink`/`StringSource` files.

## Control Flow

Customized collector tests build ordered internal keys with puts, deletes, and single deletes, finish a table, read table properties back from the in-memory file, then assert custom properties and type counters. The tests run both user-key adapter and direct internal collector modes, and both modern and legacy collector callbacks. Internal-key property tests build a second key set with deletes, single delete, and merge operands, then verify built-in deleted/merge counts and sanitized user collectors where applicable.

## State and Persistence Behavior

Tables are built entirely in memory but exercise real table metadata serialization and parsing for block-based and plain table magic numbers. The custom collector records count of keys starting with `A`, entry type counts, and file-size-change observations. Sanitization wraps public collectors into internal collectors to persist compatible properties.

## Dependencies and Integration Points

The test depends on DB options, immutable/mutable CF options, table factories, block flush policy, table builders, metadata readers, internal key comparator, and RocksDB test harness. It is the direct regression suite for `table_properties_collector.{h,cc}` and related option sanitization.

## Risks and Test Signals

The file signals expected behavior for collector context fields, backwards-compatible `Add`, delete and merge property decoding, table-format parity, and file-size monotonicity. Gaps remain around timestamp collector behavior, malformed internal keys, malformed varint properties, and collector `NeedCompact` propagation.
