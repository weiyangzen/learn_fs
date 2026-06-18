# sources/storage-engines/wiredtiger/test/suite/test_layered_prepare02.py

## Purpose

This file tests forward iteration after `search()` or `search_near()` returns `WT_PREPARE_CONFLICT` on a layered follower cursor. The expected behavior is that subsequent `next()` calls start from a clean cursor state and return the correct stable rows.

## Important APIs, Types, and Functions

Scenarios choose between `search` and `search_near`. Helpers `safe_next`, `safe_search`, and `safe_search_near` normalize prepare-conflict exceptions into return codes. `_setup_follower` creates a stable checkpoint with keys `1`, `2`, `3`, opens a follower, prepares an ingest update on one key, and returns the sessions and cursor needed by each test.

## Control Flow

The first test positions the cursor at key `3`, then searches key `2` and hits a prepare conflict. After rolling back the prepare, `next()` must return all stable keys from the beginning. The second test first conflicts on `next()` at key `1`, then conflicts again via `search` or `search_near` on the same key, rolls back the prepare, and verifies full forward iteration.

## State, Persistence, and Dependencies

The test relies on persisted stable records from a leader checkpoint plus unresolved prepared follower ingest updates. It uses `precise_checkpoint=true`, timestamped checkpoint transfer, prepared transactions, and read timestamps that cover the prepare. Dependencies are `wiredtiger`, `wttest`, `helper_disagg`, and `wtscenario`.

## Risks and Test Signals

The risk is that a conflicting point lookup preserves an old position or partially initialized layered merge state, causing later scans to skip keys. Exact `got == stable_keys` assertions after rollback provide the signal. Running both `search` and `search_near` is important because those APIs can position cursors differently internally.
