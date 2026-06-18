# sources/storage-engines/tikv/tests/integrations/raftstore/test_stale_read.rs

## Purpose
This file validates stale-read behavior with resolved timestamps and lifecycle changes. It ensures follower stale reads work at historical timestamps, timestamp zero is handled safely, resolved-ts advances after membership changes, leadership transfer, and splits, and destroyed peers lose read-progress state.

## Important APIs, Types, and Functions
It uses gRPC `TikvClient`, `kvrpcpb::Context`, `Op`, test `PeerClient` helpers, `new_mutation`, `must_kv_write`, `must_kv_read_equal`, `region_read_progress.get_resolved_ts`, and `ReadableDuration` configuration for resolved-ts advancement.

## Control Flow
`test_stale_read_with_ts0` enables resolved-ts, writes two versions, reads the exact historical values from a follower with `stale_read` set, asserts follower read at ts 0 returns not-leader, and leader read at ts 0 returns not-found. `test_stale_read_resolved_ts_advance` checks resolved-ts increases across initial write, add-peer, transfer-leader, and split. `test_resolved_ts_after_destroy_peer` removes a peer and asserts its region read progress is gone after destroy.

## State and Persistence Behavior
The tests inspect in-memory `store_metas` region read progress rather than disk state. They also depend on committed MVCC versions being persisted and readable through stale-read gRPC APIs at requested timestamps.

## Dependencies and Integration Points
This file integrates resolved-ts workers, stale-read request context, gRPC client routing, PD membership changes, split, transfer-leader, and peer destroy cleanup.

## Risks
Resolved-ts bugs can return stale values outside the safe timestamp, reject valid follower reads, or leak read-progress state for destroyed peers. The resolved-ts advancement loops are timing-sensitive and can timeout if background advancement stalls.

## Test Signals
Signals include exact historical stale-read values, not-leader and not-found behavior for timestamp zero, resolved-ts monotonic advancement on every peer in a region, and `None` for destroyed peer read progress.
