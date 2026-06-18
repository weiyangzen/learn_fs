<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/password_windows.go -->
# sources/sync-backup/kopia/cli/password_windows.go

## Purpose
Registers Windows-specific password persistence flag support.

## Important APIs, Types, And Functions
Defines `App.setupOSSpecificKeychainFlags`, adding `--use-credential-manager`, default true, bound to `c.keyRingEnabled`.

## Control Flow
The function participates in normal app setup; actual credential manager reads/writes are implemented elsewhere.

## State And Persistence Behavior
It mutates only CLI flag state. Persistent secret behavior follows later from `keyRingEnabled`.

## Dependencies And Integration Points
Depends on Kingpin and Windows build-tag selection.

## Risks And Edge Cases
Default-on behavior can surprise tests or automation that expects no persistent credentials. Flag naming differs from other OSes.

## Test Signals
Windows build/CLI tests should verify the flag exists, defaults true, and disables credential manager when false.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/password_windows.go -->
