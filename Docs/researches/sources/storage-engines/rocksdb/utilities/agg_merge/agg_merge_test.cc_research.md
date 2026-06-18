# sources/storage-engines/rocksdb/utilities/agg_merge/agg_merge_test.cc

## Purpose

This GTest file provides DB-level coverage for the experimental aggregation merge operator. It verifies that encoded aggregate operands survive normal RocksDB writes, flushes, compactions, full merges, partial merges, and failure cases.

## Important APIs, types, and functions

`AggMergeTest` derives from `DBTestBase`. The test registers `SumAggregator`, `Last3Aggregator`, and `MultipleAggregator`, installs `GetAggMergeOperator()` into `Options::merge_operator`, and uses `EncodeHelper`, `EncodeAggFuncAndPayloadNoCheck`, `EncodeAggFuncAndPayload`, `ExtractAggFuncAndValue`, and `ExtractList`.

## Control flow

The main test writes several keys. It merges three `sum` operands into `foo`, list operands into `bar` with a flush boundary, uses an unnamed Put followed by sum merges for `foo2`, switches from multiplication to sum on `bar2`, tests function switching across partial-merge opportunities on `foo3`, merges after flush and compaction on `foo4`, then validates unregistered function and invalid payload paths.

## State and persistence behavior

The test opens a real RocksDB test DB with fsync enabled through `DBTestBase`. Flush and compact operations force merge operands into persisted SST state, so the test checks both in-memory and persisted merge paths. The global aggregator registry is populated at test start and then reused by the singleton operator.

## Dependencies and integration points

The file depends on RocksDB test infrastructure, options, public agg-merge APIs, the internal implementation header, and test aggregators from `test_agg_merge.h`. The `main` installs the RocksDB stack trace handler and runs all GTests.

## Risks

Because `AddAggregator` uses a global map and duplicate registration returns OK without replacement, adding more tests in this process can inherit prior registration state. Assertions compare fully encoded strings, which is good for format coverage but means intentional encoding changes require coordinated test updates. The test covers representative aggregators but not concurrency or duplicate registration behavior.

## Test signals

Passing this test signals that full merge, partial merge, function switching, unnamed base values, compaction interaction, error packing, and list decoding still match the implementation contract.
