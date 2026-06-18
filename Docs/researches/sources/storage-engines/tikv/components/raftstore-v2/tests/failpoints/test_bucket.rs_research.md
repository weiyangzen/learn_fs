# sources/storage-engines/tikv/components/raftstore-v2/tests/failpoints/test_bucket.rs

## Purpose
This failpoint test validates bucket refresh behavior during a split race where the new split peer's apply scheduler is delayed. It ensures bucket metadata sent immediately after split can still be installed once the peer storage path becomes ready.

## Important APIs, Types, and Functions
- `test_refresh_bucket()` uses `split_region_and_refresh_bucket()` from the shared cluster helper.
- It reads `RegionLocalState.tablet_index` from the raft engine and expects the initial region at `RAFT_INIT_LOG_INDEX`.
- Failpoint `delay_set_apply_scheduler` sleeps during apply-scheduler setup to widen the race.

## Control Flow
The test starts a default one-node cluster, fetches region 2 and its peer, waits for current-term apply, enables the scheduler-delay failpoint, splits region 2 at `k22`, immediately refreshes buckets for the new region 1000, then polls debug info until bucket keys appear.

## State and Persistence Behavior
It checks persisted raft-engine region state only for the pre-split tablet index. The key behavior is in-memory bucket metadata propagation across the delayed apply-scheduler installation, eventually visible through `RegionMeta.bucket_keys`.

## Dependencies and Integration Points
The test integrates split admin commands, store-router bucket refresh, raftstore bucket metadata, raft-engine state reads, and the peer debug-info query path.

## Risks and Edge Cases
- Bucket refresh can arrive before the split peer's scheduler/storage is fully initialized.
- Losing the refresh would leave `bucket_keys` empty despite PD/autosplit updates.
- The test polls with a timeout because the failpoint uses real sleep and async scheduling.

## Test Signals
Success is `bucket_keys.len() == 4`, including region start/end keys plus the two refreshed bucket boundaries.
