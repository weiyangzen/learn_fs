# sources/sync-backup/kopia/repo/format/upgrade_lock_intent_test.go

## Purpose
Validates upgrade lock intent mutation, validation, timing, and clone behavior.

## Important APIs, Types, And Functions
Tests include `TestUpgradeLockIntentUpdatesWithAdvanceNotice`, `TestUpgradeLockIntentUpdatesWithoutAdvanceNotice`, `TestUpgradeLockIntentValidation`, `TestUpgradeLockIntentImmediateLock`, `TestUpgradeLockIntentSufficientAdvanceLock`, `TestUpgradeLockIntentInSufficientAdvanceLock`, `TestUpgradeLockIntentUpgradeTime`, and `TestUpgradeLockIntentClone`.

## Control Flow
Tests construct lock intents with controlled times and durations, then assert allowed advance-notice extensions, rejected owner mismatch or earlier upgrade time, validation failures for missing fields, lock/writer-drained booleans at key timestamps, and upgrade-time results for immediate and advance-notice modes.

## State And Persistence
All state is in-memory `UpgradeLockIntent` structs; no repository storage is used.

## Dependencies And Integration Points
Uses `clock.Now` and public `format` package APIs. It locks down semantics used by repository open/write paths and format manager upgrade methods.

## Risks And Edge Cases
The tests include a panic case for invalid negative timeout inputs, documenting that callers must validate before calling timing logic on untrusted data. Sufficient advance-notice update can temporarily unlock a previously drained lock, and the test codifies that behavior.

## Test Signals
Coverage is strong for timing math and update policy. It does not test JSON serialization, which is handled indirectly through format manager tests.
