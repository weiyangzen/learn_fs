# sources/sync-backup/borg/src/borg/testsuite/storelocking_test.py

## Purpose
Tests Borg store-backed locking semantics for exclusive and non-exclusive locks. It verifies context-manager acquisition, lock conflict behavior, stale lock cleanup, break-lock behavior, and lock migration across process identity changes.

## Important APIs, Types, and Functions
Uses `borgstore.store.Store`, `Lock`, `NotLocked`, `LockTimeout`, `ID1`, `ID2`, and the `lockstore` fixture. Test methods cover `got_exclusive_lock`, `acquire`, `release`, `break_lock`, `refresh`, `_get_locks`, `_find_locks`, and `migrate_lock`.

## Control Flow
The fixture creates a temporary store with lock configuration and destroys it after use. Tests acquire locks in nested contexts, expect timeouts for incompatible locks, allow double shared locks, assert releasing an unheld lock fails, refresh after age thresholds, then let stale locks expire.

## State and Persistence Behavior
Lock state is stored under the store's `locks/` namespace. Refresh creates new lock keys, stale discovery removes expired locks, and migration rewrites lock identity from old host/pid tuple to a new tuple.

## Dependencies and Integration Points
Integrates object-store primitives with repository/session coordination. It covers the behavior Borg depends on to prevent concurrent writers and permit shared readers.

## Risks and Test Signals
Risks include stale lock buildup, split-brain exclusive locks, shared/exclusive conflict mistakes, and PID changes after daemonization. Signals are raised `LockTimeout`/`NotLocked`, lock key set changes after refresh, empty store lock list after stale cleanup, and hostid changes after migration.
