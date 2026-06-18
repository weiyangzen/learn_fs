# sources/storage-engines/wiredtiger/test/suite/test_prepare42.py

## Purpose

Tests rolled-back prepared inserts becoming deletes through rollback tombstones, including a case where the prior stop point is globally visible.

## Important APIs, Control Flow, and State

`test_prepare_insert_rollback` inserts committed keys 1 to 19, prepares insert of key 20, rolls it back at timestamp 45, verifies early checkpoint writes no prepared content, advances stable to prepare timestamp 35 and expects prepared time-window write, evicts, advances stable to rollback timestamp, checkpoints no prepared content, evicts again, and verifies key 20 is not found. The second test first deletes key 19 at timestamp 25, makes the delete stable and globally visible by moving oldest, prepares a new insert for key 19, rolls it back, and follows the same stable/eviction progression.

## Dependencies, Risks, and Test Signals

Dependencies are preserve-prepared stats, debug page eviction, oldest/stable timestamp movement, and `WT_NOTFOUND`. Risks are failure to materialize or clean rollback tombstones when no live base update remains. Signals are staged checkpoint stat transitions and final not-found reads.
