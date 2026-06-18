<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/sst_partitioner.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/sst_partitioner.rs

## Purpose
`sst_partitioner.rs` adapts generic `engine_traits` SST partitioner factories and partitioners to RocksDB's `SstPartitionerFactory` and `SstPartitioner` traits.

## Important APIs, Types, and Functions
`RocksSstPartitionerFactory<F>` wraps an `engine_traits::SstPartitionerFactory`. Its `create_partitioner` translates `rocksdb::SstPartitionerContext` into `engine_traits::SstPartitionerContext`. `RocksSstPartitioner<P>` wraps an `engine_traits::SstPartitioner` and maps `should_partition` requests/results plus `can_do_trivial_move`.

## Control Flow
RocksDB calls the factory with compaction context. The adapter clones next-level boundary/size vectors and forwards the converted context. When RocksDB asks whether to partition, the adapter builds a request from previous/current user keys and output size, forwards it, and converts `Required` or `NotRequired` back to RocksDB.

## State and Persistence Behavior
The adapter itself has no persistence. It influences RocksDB compaction output file boundaries and trivial-move decisions, which affects SST layout.

## Dependencies and Integration Points
It is used by CF option code that installs an `engine_traits::SstPartitionerFactory` into RocksDB options. It depends on matching semantics between RocksDB and `engine_traits` request/context structs.

## Risks and Edge Cases
The adapter clones boundary vectors on creation, so large boundary lists can cost memory. Semantic drift between RocksDB and `engine_traits` fields would produce bad partitioning decisions. Trivial-move behavior is delegated entirely to the wrapped implementation.

## Test Signals
Tests should use a mock partitioner to verify context translation, result mapping, and trivial-move delegation for full/manual compaction and next-level boundary cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/sst_partitioner.rs -->
