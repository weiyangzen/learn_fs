# sources/storage-engines/tikv/tests/integrations/raftstore/test_split_region.rs

## Purpose
This large integration file validates raftstore region split behavior across manual split, auto split, epoch mismatch, bucket metadata refresh, delayed split/commit, stale peers, snapshots around split, in-memory pessimistic locks, read-index interaction, and raft-state recovery for newly split regions.

## Important APIs, Types, and Functions
Core APIs include `Cluster::must_split`, `split_region`, PD `must_split_region`, `must_merge`, `must_add_peer`, `must_remove_peer`, `RegionPacketFilter`, `Callback::write`, `WriteResponse`, `AdminRequest`/`BatchSplitRequest`, `Bucket`, `BucketRange`, and raftstore v2 `QueryResult`. Local helpers/filters include `EraseHeartbeatCommit`, `EraseHeartbeatContext`, `check_cluster!`, `test_split_epoch_not_match`, and constants `REGION_MAX_SIZE` / `REGION_SPLIT_SIZE`.

## Control Flow
Basic tests write keys on both sides of a split key, split, then assert old/new region IDs and key ranges match left-derive or right-derive rules. Auto-split tests configure small region thresholds, write/flush data until size thresholds are crossed, then assert PD observes new regions and split keys align with data size. Epoch mismatch tests send old, middle, and too-new epochs and validate current-region hints. Later tests delay follower split by erasing heartbeat commit, suppress snapshots while split is pending, run split during pending read-index, and restart nodes whose new-region raft state was not persisted.

## State and Persistence Behavior
The tests inspect KV CFs, `CF_RAFT` region local state, raft engine state, bucket versions, removed peer records, snapshot directories, and pessimistic lock in-memory tables. They verify split updates local key ranges, preserves data placement, cleans or preserves removed-record metadata as expected, moves in-memory locks to the correct child region, reconstructs missing raft state after restart, and lets snapshot apply overwrite incomplete split-initialized raft state.

## Dependencies and Integration Points
The file integrates raftstore/v2 routing, PD region metadata and split scheduling, RocksDB CF scans, raft engine reads, bucket split-check logic, merge logic, lease-read/read-index flow, transaction lock extensions, and test fail/timing helpers. It also depends on harness key-size writers such as `put_till_size` and `put_cf_till_size`.

## Risks
Region splitting is a high-blast-radius path. Regressions can produce wrong region boundaries, stale epoch hints, leader-election stalls, missing snapshot suppression, incorrect bucket metadata, lost pessimistic locks, or missing raft state after restart. Many tests are timing dependent and use sleeps around ticks, split checks, and snapshot wait windows, so slow environments can create false negatives.

## Test Signals
Signals include PD region range comparisons, `key_not_in_region` and `epoch_not_match` errors, exact returned current-region lists, region split counts, engine-level key presence/absence, no unexpected snapshot notifications, `QueryResult::Response` with an error after split during read-index, nonempty removed records, and successful writes after raft-state recovery.
