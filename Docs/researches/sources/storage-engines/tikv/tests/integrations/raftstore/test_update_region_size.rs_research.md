# sources/storage-engines/tikv/tests/integrations/raftstore/test_update_region_size.rs

## Purpose
This file tests whether raftstore updates PD's approximate region size after RocksDB compaction finishes.

## Important APIs, Types, and Functions
It uses `MiscExt::flush_cfs`, cluster `batch_put`, `compact_data`, PD `get_region_approximate_size`, `must_split`, and raftstore config knobs `pd_heartbeat_tick_interval`, `split_region_check_tick_interval`, and `region_split_check_diff`.

## Control Flow
The test configures frequent heartbeat and split checks, writes thousands of keys in batches with flushes to create multiple SSTs, splits the initial region at `k2000`, records approximate size for the left region from PD, compacts data, waits, then reads approximate size again and expects it to differ.

## State and Persistence Behavior
The file directly forces RocksDB flushes and compaction, using PD's stored approximate region size as the observable state. The data is persisted through normal raft writes before compaction triggers raftstore's compaction-finished path.

## Dependencies and Integration Points
It integrates RocksDB flush/compaction callbacks, raftstore region size tracking, split-check configuration, PD heartbeat reporting, and single-node server cluster operation.

## Risks
If compaction-finished hooks fail to refresh region size, PD may schedule based on stale size information, affecting splitting and balancing decisions. The test depends on compaction changing approximate size enough to be visible after a fixed sleep.

## Test Signals
The key signal is `old_region_size != new_region_size` after `cluster.compact_data()` and heartbeat propagation.
