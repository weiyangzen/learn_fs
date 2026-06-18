# sources/storage-engines/rocksdb/utilities/cassandra/merge_operator.h

## Purpose
This header declares `CassandraValueMergeOperator`, the RocksDB merge operator that applies Cassandra row-value reconciliation rules.

## Important APIs, Types, and Functions
The class derives from `MergeOperator` and overrides `FullMergeV2`, `PartialMergeMulti`, `Name`, `AllowSingleOperand`, and `ShouldMerge`. The constructor accepts `gc_grace_period_in_seconds` and optional `operands_limit`. `kClassName()` returns the stable option-loading name `CassandraValueMergeOperator`.

## Control Flow
The header defines policy hooks used by RocksDB's merge engine. `AllowSingleOperand` returns true so a single operand may be passed through merge processing. `ShouldMerge` requests operand merging when `operands_limit` is positive and the operand count reaches that threshold.

## State and Persistence Behavior
The only stored state is `CassandraOptions options_`, carrying tombstone GC and operand-limit settings. The persisted state is outside the class in encoded Cassandra row values; merge calls read and rewrite those values.

## Dependencies and Integration Points
It depends on RocksDB merge APIs, `Slice`, and `utilities/cassandra/cassandra_options.h`. The class name and options registration in the `.cc` file tie it to RocksDB's customizable/options system.

## Risks and Edge Cases
`ShouldMerge` is disabled when `operands_limit` is zero, so merge operands can accumulate until RocksDB's other merge triggers act. The header promises Cassandra row merge semantics but does not expose input validation or error-reporting controls. Any class-name change would break string-based configuration compatibility.

## Test Signals
Tests should verify the merge operator can be selected by name/options, honors `operands_limit`, allows single operands, and produces encoded rows compatible with `RowValue::Deserialize`.
