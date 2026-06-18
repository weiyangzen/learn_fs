# sources/storage-engines/wiredtiger/test/suite/test_prepare46.py

## Purpose

Regression test for preserving a prepared cell after eviction happens while the prepare timestamp is still unstable.

## Important APIs, Control Flow, and State

The test commits key 1 at timestamp 20, sets stable to 25 below the upcoming prepare timestamp, opens a concurrent writer transaction to pin transaction state, then prepares a fresh insert for key 2 at timestamp 30 and rolls it back at timestamp 50. Eviction at stable 25 should defer the rollback tombstone instead of marking it written. After the blocker closes and stable advances to 35, checkpoint must write `rec_time_window_prepared=True`. When stable advances to 55, checkpoint should no longer write prepared content. Reads at timestamp 20 still find key 1 throughout.

## Dependencies, Risks, and Test Signals

Dependencies are preserve-prepared config, prepared IDs, concurrent sessions, release eviction, and checkpoint stats. The risk is poisoning later reconciliation by selecting the tombstone before prepare timestamp is stable. Signals are prepared stat true at stable 35 and false at stable 55.
