<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_garbage_meter_test.cc -->
# sources/storage-engines/rocksdb/db/blob/blob_garbage_meter_test.cc

## Purpose
Tests `BlobGarbageMeter` accounting for ordinary blob indexes, non-blob values, malformed input, TTL/inlined indexes, and wide-column entities with multiple blob references.

## Important APIs, Types, and Functions
`MakeBlobIndex` encodes and decodes a test blob reference. `MeasureGarbage` constructs descriptors with expected physical byte sizes, feeds inflow/outflow combinations, and checks per-file counters. Other tests exercise `ProcessInFlow`, `ProcessOutFlow`, and the public `flows` map under specific value types.

## Control Flow
The main test builds internal keys of type `kTypeBlobIndex`, encodes `BlobIndex` values, conditionally processes them as inflow and outflow, then validates two tracked files: one with no additional garbage and one with missing outflow. Wide-column testing serializes V2 columns with blob references, then verifies that a removed column blob becomes garbage while the retained default blob does not.

## State and Persistence Behavior
The suite uses in-memory strings and `BlobGarbageMeter` state only. It validates byte accounting based on blob value size plus record-header/key adjustment rather than external file state.

## Dependencies and Integration Points
The tests depend on `BlobIndex`, blob log format, RocksDB internal keys, wide-column serialization, and the test harness. They model compaction input/output streams without invoking the full compaction subsystem.

## Risks and Edge Cases
The corrupt-key and corrupt-index tests ensure parse failures are not silently ignored. `InlinedTTLBlobIndex` documents the meter's non-TTL assumption. `WideColumnEntity` verifies that multiple blob indexes in one value are independently counted, a path easy to miss if only `kTypeBlobIndex` is tested.

## Test Signals
Coverage signals are direct assertions on `BlobStats`, `BlobInOutFlow::IsValid`, `HasGarbage`, `GetGarbageCount`, and `GetGarbageBytes`, plus `ASSERT_NOK` for invalid inputs.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/blob/blob_garbage_meter_test.cc -->
