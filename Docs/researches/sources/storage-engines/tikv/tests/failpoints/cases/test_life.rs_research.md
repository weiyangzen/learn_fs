# sources/storage-engines/tikv/tests/failpoints/cases/test_life.rs

## Purpose
This small raftstore-v2-only test verifies peer GC behavior when a store has been tombstoned or stopped during peer removal.

## Important APIs, Types, and Functions
- `test_gc_peer_on_tombstone_store` is parameterized with `test_raftstore_v2::new_server_cluster`.
- It uses `configure_for_merge`, `gc_peer_check_interval`, `disable_default_operator`, `must_remove_peer`, `stop_node`, and `must_empty_region_removed_records`.
- `mock_store_refresh_interval_secs` forces immediate invalidation of store address cache.

## Control Flow
The test creates a three-store server cluster, writes data, transfers leadership to store 1, isolates store 3, and removes store 3's peer from the region. It then invalidates the store address cache, stops node 3, clears send filters, waits several GC peer intervals, and asserts removed-region records are empty.

## State and Persistence Behavior
The state under observation is raftstore's region removed-record bookkeeping for a peer on a stopped/tombstone store. The expected behavior is that GC does not keep stale removed-records or require a live address for the tombstoned store.

## Dependencies and Integration Points
The test integrates PD peer removal, raftstore GC peer ticks, store address cache refresh, isolation filters, and server-cluster shutdown behavior.

## Risks and Test Signals
The primary risk is leaked or stuck removed-region metadata after store tombstone handling. The final `must_empty_region_removed_records` assertion is the test signal; timing depends on the configured 500 ms GC interval.
