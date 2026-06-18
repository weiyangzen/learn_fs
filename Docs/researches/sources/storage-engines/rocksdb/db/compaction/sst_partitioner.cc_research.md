<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/sst_partitioner.cc -->
# sources/storage-engines/rocksdb/db/compaction/sst_partitioner.cc

## Purpose
This file implements the fixed-prefix SST partitioner and factory registration. The partitioner requests output file boundaries when adjacent user keys differ in their first `len_` bytes, enabling compaction output files to be partitioned by fixed key prefix.

## Important APIs, Types, and Functions
`SstPartitionerFixedPrefixFactory` registers the configurable `length` option in its constructor, creates `SstPartitionerFixedPrefix` instances, and is exposed through `NewSstPartitionerFixedPrefixFactory`. `SstPartitionerFixedPrefix::ShouldPartition` compares truncated previous/current user keys and returns `kRequired` or `kNotRequired`. `CanDoTrivialMove` reuses the same logic to determine whether an input file's smallest/largest keys remain within one fixed prefix. `SstPartitionerFactory::CreateFromString` registers built-in factories once and loads a shared object/factory from string.

## Control Flow
`ShouldPartition` copies the previous and current user key slices, caps each slice size at `len_`, compares them, and requires a split when the fixed prefixes differ. `CanDoTrivialMove` builds a `PartitionerRequest` from smallest/largest user keys and treats no required split as trivial-move-compatible. Factory string creation uses `std::call_once` to register `SstPartitionerFixedPrefixFactory::kClassName()` with the default `ObjectLibrary`, then calls `LoadSharedObject`.

## State and Persistence Behavior
The only persistent configuration is the factory's `len_` option as part of RocksDB options serialization/configuration. The partitioner itself has no durable state; it influences how compaction/table-builder output is split into SST files.

## Dependencies and Integration Points
The file depends on `rocksdb/sst_partitioner.h`, customizable utilities, object registry, and options type descriptors. It integrates with compaction output file cutting, trivial move decisions, options parsing, custom object loading, and any user configuration that names the fixed-prefix partitioner.

## Risks and Edge Cases
A zero prefix length means all keys share the empty prefix, so partitioning is never required. If keys are shorter than `len_`, their full key is compared. The implementation mutates local `Slice::size_` copies, not underlying keys. Trivial-move eligibility is only prefix-based and does not check other compaction constraints.

## Test Signals
Relevant tests should assert partition decisions across equal/different prefixes, short keys, zero length, options-string factory creation, and trivial-move compatibility. Downstream compaction tests can observe output file boundaries created by the partitioner.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/db/compaction/sst_partitioner.cc -->
