# sources/storage-engines/wiredtiger/test/suite/test_prepare22.py

## Purpose

Tests prepare rollback followed by rollback-to-stable in a normal eviction path without forced eviction failure.

## Important APIs, Control Flow, and State

The test parameterizes key format and whether a committed delete exists. It inserts value A at timestamp 10, value B at 20, optionally removes at 30, prepares value C at 40, evicts the page with `ignore_prepare=true` at timestamp 20, checkpoints to persist history-store state, rolls back the prepare, sets stable to 30, and calls `rollback_to_stable`. It then evicts again and verifies reads at timestamps 10 and 20 still return A and B, with timestamp 30 returning not found for delete scenarios.

## Dependencies, Risks, and Test Signals

Dependencies are WiredTiger rollback-to-stable, release eviction, checkpoints, and `WT_NOTFOUND`. The risk is rollback-to-stable losing history after an aborted prepared update was evicted. Signals are pre/post RTS eviction and timestamp readback.
