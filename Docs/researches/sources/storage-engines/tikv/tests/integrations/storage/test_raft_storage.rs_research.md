# sources/storage-engines/tikv/tests/integrations/storage/test_raft_storage.rs

## Purpose
This file tests TiKV's transactional and raw storage APIs when backed by raftstore. It covers basic MVCC operations, leader lease reads, stale/wrong region and store errors, leader-term validation, automatic GC across split regions, and raw atomic operations.

## Important APIs, Types, and Functions
`new_raft_storage` creates a one-store `SyncTestStorageApiV1<SimulateEngine>` and request `Context`. `write_test_data` and `check_data` help auto-GC validation across leaders and regions. Tests call storage APIs such as `get`, `prewrite`, `commit`, `rollback`, `scan`, `scan_locks`, `raw_get`, `raw_put`, `raw_batch_put_atomic`, `raw_compare_and_swap_atomic`, and `raw_batch_delete_atomic`.

## Control Flow
The basic tests write MVCC values, commit them, then mutate context fields to assert region/store mismatch errors. Leader-change tests capture a term, move leadership twice, and verify not-leader/stale-command behavior. Auto-GC builds per-store storage handles, starts auto GC with callbacks, writes three timestamp generations, splits regions, advances the PD safe point, waits for one GC round per store, and checks old versions are gone while newer versions remain. Atomic tests write raw values and exercise compare-and-swap success, failure, delete, and batch delete.

## State, Persistence, and Dependencies
State spans raftstore region metadata, peer/store IDs, MVCC CF contents, PD safe point, and GC worker state. It depends on `test_raftstore`, `test_storage`, TiKV storage error types, `AutoGcConfig`, and error-code matching for stale commands.

## Integration Points, Risks, and Test Signals
The tests integrate storage API calls with raft routing, leader lease, region splits, PD safe point, GC workers, and raw atomic raft commands. Signals include exact returned values, expected structured errors (`store_not_match`, `stale_command`), callback counts, and absence/presence of old MVCC versions. Risks are timing sensitivity in GC and leader lease sleeps.
