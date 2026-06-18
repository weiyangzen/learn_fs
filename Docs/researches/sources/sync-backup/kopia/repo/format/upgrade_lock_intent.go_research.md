# sources/sync-backup/kopia/repo/format/upgrade_lock_intent.go

## Purpose
Defines the upgrade lock intent data model and timing rules used to drain repository writers before a format upgrade.

## Important APIs, Types, And Functions
`UpgradeLockIntent` stores owner ID, creation time, advance notice, IO drain timeout, status poll interval, message, and max permitted clock drift. Methods are `Update`, `Clone`, `Validate`, `UpgradeTime`, `totalDrainInterval`, and `IsLocked`.

## Control Flow
Validation requires owner, creation time, positive IO drain timeout, poll interval not exceeding drain timeout, message, positive clock drift, and if advance notice is set, it must exceed total drain interval. Updates require the same owner, preserve whether advance notice was originally set, and only allow extending upgrade time. `UpgradeTime` is either creation plus advance notice or creation plus total drain interval. `IsLocked` reports immediate lock when advance notice is insufficient, otherwise lock begins at `advanceNotice - totalDrainInterval`, and writers are drained at `UpgradeTime`.

## State And Persistence
Lock intents are serialized inside encrypted repository config. The methods themselves are pure except for returning clones.

## Dependencies And Integration Points
Used by format manager upgrade operations and repository availability checks. Depends only on `time` and `pkg/errors`.

## Risks And Edge Cases
Invalid negative timing values can make `IsLocked` panic when writers appear drained but lock is false; validation is expected before persistence. Update rules currently only allow advance-notice extension, not owner changes or earlier upgrade time.

## Test Signals
`upgrade_lock_intent_test.go` covers validation errors, update restrictions, immediate/sufficient/insufficient advance lock timing, upgrade time calculation, nil clone/lock behavior, and the panic invariant.
