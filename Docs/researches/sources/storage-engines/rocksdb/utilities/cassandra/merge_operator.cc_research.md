# sources/storage-engines/rocksdb/utilities/cassandra/merge_operator.cc

## Purpose
This file implements RocksDB's `MergeOperator` for Cassandra row values. It turns existing values and merge operands into `RowValue` objects, merges them according to Cassandra timestamp/tombstone rules, optionally collects tombstones, and writes the merged binary value back to RocksDB.

## Important APIs, Types, and Functions
The file defines `merge_operator_options_info`, registering `CassandraOptions` fields `gc_grace_period_in_seconds` and `operands_limit` for RocksDB's options infrastructure. `CassandraValueMergeOperator` constructs its option object and calls `RegisterOptions`.

`FullMergeV2` handles full merge requests with an optional existing value and a list of operands. `PartialMergeMulti` merges only operands and is used to reduce queued merge operands before a base value is read.

## Control Flow
`FullMergeV2` clears the output, deserializes the existing value if present, deserializes every operand, calls `RowValue::Merge`, removes collectable tombstones using the configured GC grace period, reserves output capacity from the merged size, serializes the result, and returns true. `PartialMergeMulti` follows the same pattern for operands only but does not perform tombstone GC cleanup.

## State and Persistence Behavior
The operator is stateless across calls except for `CassandraOptions`. It reads persisted binary row values from slices and writes a new persisted binary value to a string owned by RocksDB's merge machinery. Full merges can physically remove collectable column tombstones, while partial merges preserve them so future full merges can still honor tombstone semantics.

## Dependencies and Integration Points
The implementation depends on RocksDB's merge operator API, option type registration, `utilities/cassandra/format.h`, and `utilities/merge_operators.h`. It is integrated by configuring a DB column family with `CassandraValueMergeOperator` or loading the operator by class name/options.

## Risks and Edge Cases
All operands are deserialized eagerly into memory, so very large operand lists can be expensive until `ShouldMerge` controls compaction frequency. Deserialization relies on asserts in the format layer rather than returning merge failure for malformed values. Partial merge omits tombstone GC by design; changing that could make deleted columns reappear incorrectly. `FullMergeV2` returns true unconditionally, so corrupt input is not reported through merge status unless it crashes/asserts.

## Test Signals
Signals should include full merge with base values, partial merge of operands, option parsing, `ShouldMerge` thresholds, row tombstone cutoff behavior, and GC grace tombstone removal. Cassandra row format tests are prerequisite because this operator trusts the format layer.
