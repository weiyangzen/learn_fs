# sources/storage-engines/tikv/components/hybrid_engine/src/observer/test_write_batch.rs

Purpose: regression tests for hybrid observable write batches mirroring disk mutations into the in-memory cache.

Important APIs/types/functions: tests `test_sequence_number_unique`, `test_write_to_both_engines`, `test_set_sequence_number`, and `test_delete_range`, using `WriteBatchWrapper`, `RegionCacheWriteBatchObserver`, failpoints, and internal key decoding.

Control flow: tests write through wrapped disk/cache batches, prepare regions, block loading via failpoint, inspect in-memory internal sequence ordering, verify disk and cache reads, reject duplicate sequence setting, and confirm delete ranges evict affected cache regions.

State and persistence: temporary RocksDB plus in-memory region cache; delete-range eviction is asynchronous and waited for eventually.

Dependencies/integration: exercises raftstore write batch wrapper, in-memory engine internals, crossbeam epoch, failpoints, and hybrid test utility.

Risks: sequence-order assertions are intentionally brittle regression checks; timing-based eventual eviction can be sensitive under slow test environments.

Test signals: this file is the main test signal for write-batch persistence/cache consistency.
