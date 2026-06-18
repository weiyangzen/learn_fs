<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_merge.rs -->
# sources/storage-engines/tikv/tests/integrations/raftstore/test_merge.rs

## Purpose
This large integration test file is the main raftstore region-merge test suite. It validates normal split/merge behavior, merge prerequisites, stale peer cleanup, learner and target-peer edge cases, snapshot interaction, pessimistic lock transfer, approximate stats updates, max-ts synchronization, v1/v2 differences, and v2 removed/merged record GC.

## Important APIs, Types, and Functions
Core helpers come from `test_raftstore`: `configure_for_merge`, `ignore_merge_target_integrity`, `configure_for_snapshot`, `must_split`, `must_merge`, `try_merge`, `merge_region`, `must_transfer_leader`, `must_region_not_exist`, `wait_log_truncated`, `wait_tombstone`, and message filters such as `IsolationFilterFactory`, `RegionPacketFilter`, `DropMessageFilter`, and `CloneFilterFactory`.

The file also uses `RegionLocalState`, `PeerState`, `ExtraMessageType`, `ConfChangeType`, `RAFT_ENABLE_UNPERSISTED_APPLY_GAUGE`, `LocksStatus`, `SnapshotExt`, `PessimisticLock`, `LastChange`, `CF_LOCK`, `CF_WRITE`, and API-version test helpers. Tests are split between `test_raftstore` and `test_raftstore_v2` via `#[test_case]`.

## Control Flow and Behavior
The base merge tests write data, split a region, verify key range enforcement, merge adjacent regions, assert epoch version increases by prepare+commit merge, confirm source peers become tombstones, and ensure post-merge writes succeed. Prerequisite tests intentionally create log gaps, admin entries, oversized log gaps, incomplete learner catch-up, reset `matched` indexes, and five-node snapshot states to ensure merge is rejected until a safe catch-up point exists.

Many scenarios isolate a store during merge and then recover it: slow learners, slow split, distributed isolation, brain split, cascade merge, target peer absent during isolation, stale learners removed before merge, and target peers removed before applying commit-merge. These tests use explicit leader placement and packet filters to create asymmetric progress, then check that recovered stores either catch up via logs/snapshot or destroy obsolete peers.

Snapshot and restart paths are covered by demotion during snapshot, empty-entry catch-up across restart, long-isolated target cleanup, stale raft messages after merge, and snapshot-based recovery of isolated stores. Transactional state is covered by transferring in-memory pessimistic locks from source to target, preserving target locks, keeping lock status in `MergingRegion` on repeated merge proposals, and allowing new writes when the log gap makes merge fail.

The v2-specific tail verifies source removed records and merged records are retained while peers are unreachable, forwarded either by target peer or by store-level GC responses, and cleaned once GC peer ticks can complete.

## State and Persistence
The tests inspect region epochs, raft/apply progress, tombstone region local state, raft log truncation, merged records, removed records, pending in-memory locks, lock CF writes, approximate size/key reports, max timestamp in the concurrency manager, and unpersisted-apply gauge state. Several cases intentionally restart the cluster or trigger snapshots to verify that merge decisions and cleanup survive persisted state boundaries.

## Dependencies and Integration Points
This suite integrates PD operators, raftstore admin commands, local reader/snapshot state, RocksDB/raft engine metadata, pessimistic transaction memory state, API version formatting, region heartbeat stats, and v1/v2 raftstore implementations. It is a high-blast-radius regression suite for region lifecycle, raft log safety, and distributed metadata cleanup.

## Risks
The file has heavy timing and topology assumptions. Failures may be flaky if leader transfer, tick intervals, snapshot generation, or filter timing changes. The riskiest behaviors are merge proceeding with unsafe log gaps, obsolete peers serving data after merge, pessimistic locks being lost or duplicated, max-ts not advancing after merge, and v2 removed/merged records leaking indefinitely.

## Test Signals
Signals include successful `must_merge`/expected `try_merge` errors, `PeerState::Tombstone`, `must_region_not_exist`, exact key presence/absence on isolated stores, lock bytes in `CF_LOCK`, `LocksStatus::MergingRegion`, changed approximate size/key metrics, advanced `max_ts`, cleaned merged/removed records, and preserved availability after network filters are cleared.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/tests/integrations/raftstore/test_merge.rs -->
