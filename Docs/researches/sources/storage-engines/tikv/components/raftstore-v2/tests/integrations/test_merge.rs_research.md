# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_merge.rs

## Purpose
This integration test validates normal raftstore-v2 region merge behavior after repeated splits. It checks tablet-index/version changes during splits, data preservation across left/right merges, chained merges, and restart recovery after the final merged region contains all keys.

## Important APIs, Types, and Functions
- `test_merge()` defines a `do_split` closure that checks tablet index increases for the source region, new regions start at `RAFT_INIT_LOG_INDEX`, and region version increments.
- It uses `split_region()` to create six adjacent regions and `merge_region()` to merge from both directions and then chain the remaining regions.
- Snapshot reads verify marker keys in each region before and after merge.

## Control Flow
Starting from region 2, the test repeatedly splits the right-hand side to create six regions. It validates each region's marker key is readable in the expected range. It merges region 1 into 2, region 6 into 5, then merges the middle chain until all data is in region 5. After restart, it reads all marker keys from the final region.

## State and Persistence Behavior
The test directly checks raft-engine region state at current and exact tablet indexes, flushed index relative to tablet index, region epoch version increments, and persisted data survival after restart. Merges must preserve data from destroyed source tablets in the target.

## Dependencies and Integration Points
It uses cluster split/merge helpers, raft-engine read-only APIs, tablet index constants, snapshots, and store id/peer constructors.

## Risks and Edge Cases
- Tablet indexes must advance for source splits and remain init for newly created tablets.
- Flushed indexes must cover the tablet index used by persisted region state.
- Merge direction must not matter; source data must appear in target for both left-to-right and right-to-left merges.
- Restart must reconstruct the final merged range with all data.

## Test Signals
Signals include tablet-index inequality/equality, version increments, flushed-index bounds, snapshot key presence before/after merge, and post-restart data presence.
