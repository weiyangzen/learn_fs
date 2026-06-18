# sources/storage-engines/wiredtiger/test/suite/test_prepare35.py

## Purpose

Tests repeated prepared inserts to the same key, including a rolled-back prepared update that leaves a globally visible tombstone before a second prepared update.

## Important APIs, Control Flow, and State

The test creates committed baseline keys 1 to 20, prepares key 21 with `prepared_id=1`, advances stable to the prepare timestamp, and verifies checkpoint writes prepared time-window metadata. It forces eviction through a debug page eviction session, rolls back the prepared insert at timestamp 35, verifies key 21 is not visible, then creates a second prepared insert to key 21 with a different prepared ID and advances stable beyond its prepare timestamp. A final checkpoint must again write prepared content.

## Dependencies, Risks, and Test Signals

Dependencies are preserve-prepared helper stats, page eviction debug, prepared IDs, and `WT_NOTFOUND`. The risk is retaining or losing tombstone/prepared state when a second prepared operation reuses a key. Signals are two `rec_time_window_prepared` checkpoints and readback after first rollback.
