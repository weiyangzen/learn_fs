# sources/storage-engines/tikv/tests/failpoints/cases/test_sst_recovery.rs

## Purpose
This suite tests TiKV's damaged SST recovery worker. It creates a cluster whose first store has a corrupted RocksDB SST spanning selected region ranges, then verifies recovery deletes damaged files only after affected peers are safely removed, preserves unrelated data, and serializes with adding peers back to the damaged store.

## Important APIs, Types, And Functions
`assert_corruption` checks engine errors contain `Corruption`. `disturb_sst_file` overwrites an SST file with invalid bytes. `compact_files_to_target_level` uses `RocksEngine::compact_files_cf` to force selected live SSTs into a target level and surface corruption. `create_tikv_cluster_with_one_node_damaged` builds a three-store `ServerCluster`, starts `RecoveryRunner` workers using each store's `store_meta`, writes three SST ranges, splits regions at `2`, `4`, and `7`, corrupts the middle `[3,5]` SST, and returns the cluster, PD client, and damaged engine.

## Control Flow
`test_sst_recovery_basic` pauses before file deletion, waits for `store_meta.get_all_damaged_region_ids()` to report two damaged regions, removes corresponding peers from store 1, proves other stores can serve the affected key, and checks the corrupted read still fails while deletion is paused. After releasing the failpoint, the corrupted key becomes absent, damaged ranges clear, live file count drops, and cluster reads still work from remaining replicas.

`test_sst_recovery_overlap_range_sst_exist` creates an additional overlapping L0 SST with updated values before removing damaged-region peers. After recovery, compaction reduces files to one while preserving non-damaged overlapping data on store 1; because store 1 no longer hosts the affected peer, cluster reads for key `4` return the newer value from other stores. `test_sst_recovery_atomic_when_adding_peer` pauses deletion, removes affected peers, attempts to add a peer back on store 1, and expects the conf change not to finish until recovery releases the store metadata lock and deletes the damaged file.

## State And Persistence Behavior
Persistent state includes RocksDB SST files, live file metadata, region replicas, and KV values across stores. In-memory state includes `store_meta.damaged_ranges` and damaged region IDs tracked by the recovery worker. Recovery must delete entire damaged SST files only after affected replicas are removed from the damaged store, and must preserve non-overlapping keys in adjacent SSTs.

## Dependencies And Integration Points
The file integrates `engine_rocks_helper::sst_recovery::RecoveryRunner`, RocksDB compaction/live-file APIs, raftstore peer membership, PD conf changes, store metadata locking, failpoints around recovery deletion, and engine `Peekable` reads.

## Risks And Edge Cases
Risks include deleting corrupted SSTs before replicas are removed, losing unaffected overlapping data, allowing conf changes to add a peer while damaged-file deletion is in progress, failing to clear damaged range metadata, or leaving RocksDB background corruption after compaction.

## Test Signals
Signals include corruption errors before recovery, `None` for corrupted keys after deletion, exact live-file counts, empty `damaged_ranges`, successful reads from healthy replicas, preserved overlapping values in store-local reads, and `must_region_not_exist`/`must_region_exist` around atomic add-peer recovery.
