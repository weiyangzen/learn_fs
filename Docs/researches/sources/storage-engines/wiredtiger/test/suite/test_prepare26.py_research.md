# sources/storage-engines/wiredtiger/test/suite/test_prepare26.py

## Purpose

Tests rollback of a prepared update, deletion of the same key, timestamp advancement, and later updates after eviction.

## Important APIs, Control Flow, and State

The test inserts value A at timestamp 10, prepares value C at 20, evicts at timestamp 10 with `ignore_prepare=true`, rolls back the prepare, deletes the key at timestamp 30, advances oldest to 30, evicts and expects not found, writes value B at 40 and C at 50, evicts again at timestamp 50, and finally verifies timestamp 30 reads not found. It runs for column and integer-row keys.

## Dependencies, Risks, and Test Signals

Dependencies are release eviction, timestamped removes/updates, oldest timestamp advancement, and `WT_NOTFOUND`. The risk is an aborted prepared update being selected as a base value after the key is deleted and rewritten. Signals are staged evictions and a final timestamped not-found assertion.
