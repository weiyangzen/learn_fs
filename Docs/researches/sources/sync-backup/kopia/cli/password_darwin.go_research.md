<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/password_darwin.go -->
# sources/sync-backup/kopia/cli/password_darwin.go

## Purpose
Registers macOS-specific password persistence flag support.

## Important APIs, Types, And Functions
Defines `App.setupOSSpecificKeychainFlags` for Darwin, adding `--use-keychain` with default true and binding it to `c.keyRingEnabled`.

## Control Flow
The function is called during app setup to expose the platform flag. Actual keychain operations are handled by password persistence code elsewhere.

## State And Persistence Behavior
It mutates only CLI flag binding state; persistent password storage is affected later when the app uses `keyRingEnabled`.

## Dependencies And Integration Points
Depends on Kingpin and app setup calling the platform-specific method selected by build tags.

## Risks And Edge Cases
Default-on behavior means macOS users may store repository passwords unless they opt out. Tests running on Darwin need account for the flag name and default.

## Test Signals
Build-tag coverage and CLI flag tests on Darwin are the relevant signals.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/password_darwin.go -->
