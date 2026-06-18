# sources/storage-engines/tikv/tests/failpoints/cases/test_replica_read.rs

## Purpose
This file is a failpoint suite for replica reads, read-index correctness, and read-index safe timestamp caching across follower lag, snapshot application, leader transfer, split, merge, destroyed peers, and lock checking.

## Important APIs, Types, and Functions
- Tests are parameterized across raftstore v1/v2 where supported; read-index-cache tests are mostly raftstore v1/server-cluster specific.
- Core helpers include `async_command_on_node`, `async_read_on_peer`, `async_read_index_on_peer`, `get_snapshot`, `get_region_read_index_safe_ts`, `make_cb_rocks`, and `block_on_timeout`.
- Important types include `Context`, `KeyRange`, `RegionLocalState`, `PeerState`, `RaftMessage`, `SnapContext`, `Snapshot`, `Lock`, and `TimeStamp`.
- Failpoints include `on_apply_write_cmd`, `before_handle_snapshot_ready_3`, `region_apply_snap`, `send_snapshot`, `apply_snap_cleanup_range`, `on_peer_collect_message_2`, `on_handle_apply_2`, `before_propose_readindex`, `skip_check_stale_read_safe`, and cache-path panic failpoints.

## Control Flow
Early tests prove follower reads wait for apply index, duplicate read-index contexts are not dropped, uninitialized peers reject reads, peers applying snapshots block or error correctly, and reads do not complete against a range cleaned for snapshot. Middle tests validate split learners know leaders quickly, read-index responses remain correct after transfer leader, batch read-index terms are current, and lock checking happens on the true leader or returns an error from false-leader situations. Later tests validate read-index safe-ts cache behavior: cache is not used while locks are present, destroyed peers do not return snapshots, split propagates safe-ts and lock checks to both child regions, merge resets safe-ts on the merged region, and leader transfer keeps safe-ts valid under new max-ts.

## State and Persistence Behavior
The suite observes raft apply index, raft log entries, region local state, read-index response terms/indexes, concurrency-manager locks, `read_index_safe_ts`, peer destruction, and snapshots. It ensures replica reads never bypass unapplied writes, uninitialized/applying peers, destroyed peers, stale ranges, or locks at/above the read timestamp. Split and merge tests ensure safe-ts metadata is reset or scoped to the correct region.

## Dependencies and Integration Points
It integrates raftstore lease-read configuration, PD peer management, raft message filters, snapshot cleanup/application, storage `async_snapshot`, concurrency manager lock checking, raft engine entry reads, and both raftstore v1/v2 read paths.

## Risks and Test Signals
Risks include stale follower reads, dropped duplicate read-index responses, invalid reads during snapshot cleanup, leader-transfer read-index term/index bugs, cache hits despite locks, safe-ts leakage across split/merge, and snapshots from destroyed peers. Signals are timeout-vs-success boundaries, explicit header errors, command type `Snap` or `Invalid`, lock-info equality, safe-ts values, and `region_not_found` errors.
