# sources/storage-engines/wiredtiger/test/suite/test_prepare47.py

## Purpose

Tests aborted prepared inserts on top of committed tombstones, ensuring reconciliation keeps a rollback fallback across multiple evictions.

## Important APIs, Control Flow, and State

The class parameterizes row and column keys under precise checkpoint/preserve-prepared. `test_aborted_prepared_with_committed_tombstone` inserts and checkpoints values, deletes them in memory, prepares replacement values, rolls back with rollback timestamp ahead of stable, advances oldest past the tombstone, evicts once below prepare timestamp and again after stable passes prepare timestamp, then asserts representative keys are not found. `test_aborted_prepared_with_lost_disk_fallback` creates an on-disk cell with start and stop timestamps, prepares insert after the cell is deleted, rolls back without appending a tombstone because the disk cell is the fallback, then performs the same two eviction rounds.

## Dependencies, Risks, and Test Signals

Dependencies are scenario key formats, release eviction, timestamped helper reads, and preserve-prepared semantics. Risks are dropping the committed tombstone or on-disk fallback, causing leaked-prepared-update assertions. Signals are no assertion during second eviction and not-found reads after rollback.
