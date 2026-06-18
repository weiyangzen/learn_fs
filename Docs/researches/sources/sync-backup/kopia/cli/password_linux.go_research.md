<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/password_linux.go -->
# sources/sync-backup/kopia/cli/password_linux.go

## Purpose
Registers Linux-specific password persistence flag support.

## Important APIs, Types, And Functions
Defines `App.setupOSSpecificKeychainFlags`, adding `--use-keyring`, default false, environment override `KOPIA_USE_KEYRING`, and binding to `c.keyRingEnabled`.

## Control Flow
The app setup exposes the flag; later password persistence chooses whether to use GNOME Keyring based on the boolean.

## State And Persistence Behavior
It changes only flag-bound app state. Any persistent secret writes occur outside this file.

## Dependencies And Integration Points
Depends on Kingpin and service `EnvName` namespacing.

## Risks And Edge Cases
Default-off differs from macOS/Windows defaults, so cross-platform behavior must be documented and tested separately.

## Test Signals
Linux CLI flag tests should verify default, environment override, and interaction with repository connect/create password persistence.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/password_linux.go -->
