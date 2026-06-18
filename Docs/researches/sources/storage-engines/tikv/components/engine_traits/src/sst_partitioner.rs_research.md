# sources/storage-engines/tikv/components/engine_traits/src/sst_partitioner.rs

Purpose: Abstracts backend SST partitioner callbacks used during compaction/output file generation.

Important APIs and control flow: `SstPartitionerRequest` describes previous/current user key and current output file size. `SstPartitionerResult` returns whether partitioning is required. `SstPartitionerContext` describes compaction mode, output level, key bounds, and next-level boundaries/sizes. `SstPartitioner` decides partitioning and trivial-move eligibility. `SstPartitionerFactory` names and creates partitioners.

State, persistence, and dependencies: Partitioners influence persistent SST output boundaries but do not persist state themselves.

Integration points, risks, and test signals: Connected through CF options and backend compaction. Risks include factory/partitioner lifetime restrictions, boundary vector alignment, trivial-move decisions that bypass desired partitioning, and backend support differences. Signals are backend compaction/partition tests and output-file shape checks.
