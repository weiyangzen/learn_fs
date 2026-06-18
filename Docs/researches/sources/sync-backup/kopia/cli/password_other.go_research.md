<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/cli/password_other.go -->
# sources/sync-backup/kopia/cli/password_other.go

## Purpose
Provides the no-op password persistence flag hook for platforms other than Windows, Linux, and Darwin.

## Important APIs, Types, And Functions
Defines `App.setupOSSpecificKeychainFlags` under build tag `!windows && !linux && !darwin`; it accepts services and app but registers no flags.

## Control Flow
Control flow is intentionally empty, so unsupported platforms do not expose platform keychain flags.

## State And Persistence Behavior
No state or persistence behavior is changed.

## Dependencies And Integration Points
Depends only on build-tag selection and Kingpin types for signature compatibility.

## Risks And Edge Cases
Users on unsupported platforms cannot enable OS keychain storage through these flags. Future platform additions need new build-tag files.

## Test Signals
Build coverage on an `other` GOOS or static analysis of build constraints is the main test signal.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/cli/password_other.go -->
