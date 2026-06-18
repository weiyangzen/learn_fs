# sources/storage-engines/wiredtiger/test/suite/test_layered_stepup05.py

## Purpose
Tests reuse of a reset layered cursor across follower-to-leader step-up with different checkpoint views and optional read timestamps.

## APIs, Types, And Functions
Defines `test_layered_stepup05`, scenarios over cursor operations (`next`, `prev`, `search`, `search_near`) and transaction modes. Helpers write timestamped checkpoints, dispatch the selected operation, and decide whether the run should see checkpoint 1 based on `read_ts`.

## Control Flow, State, And Persistence
The leader writes checkpoint 1, a follower advances to it and opens then resets a cursor, the leader writes checkpoint 2 with new keys and an updated value, the follower advances again, the leader closes, and the follower is promoted. The existing cursor is then used inside or outside a transaction. Persistence expectations are tied to stable checkpoint visibility and read timestamp selection.

## Dependencies, Integration, Risks, And Test Signals
Depends on disaggregated checkpoint pickup, cursor reset semantics, read timestamps, and layered cursor stable/ingest coordination. Risks include stale stable cursor state after step-up and incorrect checkpoint selection for reset cursors. Assertions validate exact keys and values for each operation under each transaction scenario.
