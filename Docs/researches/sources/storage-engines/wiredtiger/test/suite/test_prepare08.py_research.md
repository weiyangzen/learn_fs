# sources/storage-engines/wiredtiger/test/suite/test_prepare08.py

## Purpose

Tests that prepared tombstones and update-then-delete chains are correctly committed or rolled back after eviction has pushed prepared content toward the data store. It covers column-store and string-row tables with byte-array values.

## Important APIs, Control Flow, and State

`test_prepare08` uses `wttest.WiredTigerTestCase`, `SimpleDataSet`, `make_scenarios`, `session.begin_transaction`, `prepare_transaction`, `commit_transaction`, `rollback_transaction`, `checkpoint`, and debug cursors with `release_evict`. Helpers bulk update, remove, and timestamp-read rows with `ignore_prepare=true`. The three tests build two tables, pin oldest/stable timestamps, load large values at timestamps 20 and 30, checkpoint, create an unresolved prepared delete or update-delete sequence, then mutate the second table to force eviction of the first. They verify older values remain visible while the prepare is unresolved, then check rollback preserves prior history and commit produces deletion visibility at the commit timestamp. One variant starts from a committed tombstone instead of a base update.

## Dependencies, Risks, and Test Signals

Dependencies are WiredTiger Python APIs, timestamp helpers, datasets, scenarios, and eviction debug config. The risk is subtle reconciliation of prepared tombstones written to disk, especially when no base update exists or multiple updates share one prepared transaction. Signals are timestamped reads, `WT_NOTFOUND`, large value pressure, checkpoints, and explicit eviction before resolution.
