# sources/storage-engines/wiredtiger/test/suite/test_layered_prepare03.py

## Purpose

This focused test verifies that a layered follower cursor resumes correctly when the very first `next()` call returns `WT_PREPARE_CONFLICT`. It protects the boundary case where there is no prior returned key or saved scan position.

## Important APIs, Types, and Functions

The class uses `disagg_test_class` and a leader connection with `precise_checkpoint=true`. `safe_next` catches `wiredtiger.WiredTigerError` and returns `wiredtiger.WT_PREPARE_CONFLICT` only for the expected conflict. The table is a layered disaggregated table with string keys and values.

## Control Flow

The leader writes stable keys `1`, `2`, `3`, advances stable to 200, and checkpoints. A follower opens and picks up the checkpoint. The follower then prepares an ingest update for key `1`, so a read-committed scan conflicts on its first `next()`. After the prepare is rolled back, the same cursor continues and must return all three stable keys in order.

## State, Persistence, and Dependencies

State spans stable checkpoint contents and an unresolved prepared update in the follower ingest tree. The reader uses `isolation=read-committed` rather than an explicit read timestamp, making the conflict path sensitive to current prepared visibility. Dependencies are limited to `wiredtiger`, `wttest`, and `helper_disagg`.

## Risks and Test Signals

The risk is losing the ability to restart a scan after an initial conflict, either by assuming a previous key exists or by leaving the cursor marked positioned. The test signal is compact and strong: first `next()` must conflict, then after rollback iteration must return exactly `['1', '2', '3']` and end with `WT_NOTFOUND`.
