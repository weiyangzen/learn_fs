# sources/storage-engines/wiredtiger/test/suite/test_prepare48.py

## Purpose

Regression test for an aborted prepared insert with a pinned concurrent writer and persisted delete fallback.

## Important APIs, Control Flow, and State

The test commits key 1 as an eviction anchor, commits key 2 then removes it, advances stable to 31, checkpoints, and force-evicts so the delete reaches disk. Oldest advances past the remove, a blocker session keeps an active writer transaction open, and an eviction session begins before the prepared transaction. Another session prepares an insert for key 2 at timestamp 40 and rolls it back at 50. Eviction below prepare timestamp must preserve the persisted delete. After stable 42, a second eviction and read assert key 2 remains not found. Stable 55 and checkpoint clean up while preserving not-found semantics.

## Dependencies, Risks, and Test Signals

Dependencies are multiple concurrent sessions, release eviction, `assert_not_found`, preserve-prepared config, and `WT_NOTFOUND`. The risk is discarding the persisted delete when an aborted prepared marker remains. Signals are not-found reads before and after rollback timestamp becomes stable.
