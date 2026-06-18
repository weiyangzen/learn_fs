# sources/storage-engines/rocksdb/utilities/agg_merge/agg_merge_impl.h

## Purpose

This internal header declares the concrete merge-operator class behind the public aggregation-merge API. It separates RocksDB's `MergeOperator` implementation details from the public experimental utility header.

## Important APIs, types, and functions

`AggMergeOperator` derives from `MergeOperator` and overrides `FullMergeV2`, `PartialMergeMulti`, `Name`, `AllowSingleOperand`, and `ShouldMerge`. It exposes `kClassName()` as `"AggMergeOperator.v1"`. Private helpers declare the nested `Accumulator`, `PackAllMergeOperands`, and `GetTLSAccumulator`. `EncodeAggFuncAndPayloadNoCheck` is declared for tests and internal error-path construction.

## Control flow

The header only declares behavior. The control path is implemented in `agg_merge.cc`: full merges aggregate existing value plus operands, partial merges aggregate only when safe, and errors pack original operands. `ShouldMerge` always returns false, leaving merge scheduling to RocksDB's standard merge machinery rather than forcing proactive merge decisions.

## State and persistence behavior

The class itself carries no member fields. State lives in the static aggregator registry, thread-local accumulator, and persisted encoded values. `AllowSingleOperand()` returns true, allowing RocksDB to invoke merge logic even with a single operand.

## Dependencies and integration points

It includes RocksDB merge and slice headers, the public `agg_merge.h`, and an unrelated Cassandra options include that appears unnecessary for this declaration. It is included by the implementation and tests under `utilities/agg_merge`.

## Risks

Because this is an internal header, changing method behavior or `Name()` can affect existing DB option compatibility and tests. The extra include increases compile coupling. The no-state class hides important global state in the implementation, so tests must account for cross-test registrations.

## Test signals

The integration test checks the operator by name only indirectly through `GetAggMergeOperator` and DB merge behavior. Compile coverage also validates that RocksDB's `MergeOperator` override signatures stay current.
