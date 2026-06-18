# sources/storage-engines/tikv/components/raftstore-v2/tests/integrations/test_split.rs

## Purpose
This integration test validates normal raftstore-v2 split behavior, including repeated splits of existing and newly created regions, tablet-index evolution, region epoch version increments, flushed-index persistence, MVCC timestamp split-key truncation, and restart survival.

## Important APIs, Types, and Functions
- `test_split()` uses `split_region()` to split region 2 into 1000, split region 2 again into 1001, split region 1000 into 1002, and split 1002 into 1003.
- It reads raft-engine `RegionLocalState` at latest and exact tablet indexes, and raft-engine flushed indexes for `CF_RAFT`.
- It uses `txn_types::Key::append_ts`/`truncate_ts` to verify encoded MVCC split key handling.

## Control Flow
The test starts from region 2 at `RAFT_INIT_LOG_INDEX`, performs splits with key-range validation through helper writes, and after each split checks region state. For source regions, tablet index must change and version increments. For new regions, tablet index starts at `RAFT_INIT_LOG_INDEX`. It then restarts and verifies each final region can read a marker key in its range.

## State and Persistence Behavior
Splits persist new region metadata, tablet indexes, region versions, and flushed-index progress in the raft engine. They also create/install tablet state for new regions. Restart validates this persisted split graph.

## Dependencies and Integration Points
It uses cluster split helper, raft-engine APIs, tablet index constants, snapshots, store peer constructors, and transaction key encoding.

## Risks and Edge Cases
- Source tablet indexes must monotonically advance across repeated splits.
- Flushed index must be at least the new tablet index to support recovery.
- New split region tablets should start at init log index.
- Encoded keys with timestamps must split on the raw key boundary.

## Test Signals
Signals include tablet-index equality/inequality, version increments, exact region state lookup by tablet index, flushed-index lower bounds, and post-restart snapshot key presence in all split regions.
