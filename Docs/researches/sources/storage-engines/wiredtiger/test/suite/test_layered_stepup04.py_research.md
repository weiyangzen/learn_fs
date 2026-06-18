# sources/storage-engines/wiredtiger/test/suite/test_layered_stepup04.py

## Purpose
Verifies that prepared transactions active on a follower at step-up time survive promotion and can be committed or rolled back correctly.

## APIs, Types, And Functions
Defines `test_layered_stepup04` with scenarios over commit versus rollback, prepare-in-checkpoint versus not, and single versus multi-table. Helpers open followers with `checkpoint_meta`, checkpoint arbitrary connections, and resolve prepared transactions through `timestamp_transaction`, `commit_transaction`, or `rollback_transaction`.

## Control Flow, State, And Persistence
Each test builds base committed data, optionally checkpoints a prepared transaction on the leader, closes the leader without a final checkpoint, opens a follower from exact checkpoint metadata, creates a matching live prepared transaction, promotes the follower via `reconfigure('disaggregated=(role="leader")')`, resolves it, checkpoints, and validates historical and post-resolution reads. Insert, update, and delete variants cover new keys, changed existing keys, and tombstones.

## Dependencies, Integration, Risks, And Test Signals
Depends on `preserve_prepared=true`, `precise_checkpoint=true`, prepared IDs, read timestamps, and layered tables. Risks are unresolved prepare state, conflict during step-up, incorrect timestamp visibility, or partial multi-table resolution. Assertions check read visibility at `ts=60` and `ts=200` for both commit and rollback outcomes.
