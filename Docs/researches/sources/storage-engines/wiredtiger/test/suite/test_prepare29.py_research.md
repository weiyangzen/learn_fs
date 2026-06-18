# sources/storage-engines/wiredtiger/test/suite/test_prepare29.py

## Purpose

Ensures updates preceding an unstable prepared tombstone are restored with valid transaction IDs after crash recovery.

## Important APIs, Control Flow, and State

The test is skipped for disaggregated storage because it relies on rollback-to-stable. It inserts a value at timestamp 100, sets stable to 200, checkpoints, removes the key in a prepared transaction at timestamp 300, evicts the key with `ignore_prepare=true`, checkpoints from another session, and simulates an unclean crash restart. After recovery, it removes the same key in a new transaction and commits at timestamp 201. Without correct transaction ID reset for restored updates, this operation would see a write conflict or rollback error.

## Dependencies, Risks, and Test Signals

Dependencies are `simulate_crash_restart`, release eviction page debug, timestamps, and scenario key formats. The risk is recovery leaving restored pre-tombstone updates with transaction IDs that conflict with future writers. The signal is successful post-recovery remove/commit.
