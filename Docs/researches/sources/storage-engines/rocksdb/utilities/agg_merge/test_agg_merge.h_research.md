# sources/storage-engines/rocksdb/utilities/agg_merge/test_agg_merge.h

## Purpose

This test header declares the concrete aggregators and encoding helper used by `agg_merge_test.cc`. It provides small, focused aggregator implementations for exercising production merge-operator behavior.

## Important APIs, types, and functions

`SumAggregator`, `MultipleAggregator`, and `Last3Aggregator` derive from `Aggregator` and implement `Aggregate`. The first two override `DoPartialAggregate()` to true explicitly, while `Last3Aggregator` inherits the default true behavior. `EncodeHelper` declares methods for integer, list, and function-plus-payload encodings.

## Control flow

The header only declares test components. Implementations in `test_agg_merge.cc` encode payloads and aggregate vectors supplied by `AggMergeOperator`.

## State and persistence behavior

No state is stored in the classes. Instances are registered in the global agg-merge registry during the test and then invoked by RocksDB merge processing. Encoded outputs become normal RocksDB values in the test DB.

## Dependencies and integration points

It includes the public merge and slice headers, public `agg_merge.h`, and the same Cassandra options include as `agg_merge_impl.h`. It is consumed by the agg-merge unit test and helper implementation.

## Risks

The explicit `DoPartialAggregate()` override on integer aggregators documents intent, but `Last3Aggregator` relies on the base default; if that default changes, tests could change behavior. Like the internal header, the Cassandra include appears unnecessary and adds compile coupling.

## Test signals

Compilation and use in `agg_merge_test.cc` signal that custom `Aggregator` subclasses can be registered and invoked through the production operator.
