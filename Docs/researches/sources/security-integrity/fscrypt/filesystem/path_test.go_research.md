# sources/security-integrity/fscrypt/filesystem/path_test.go

## Purpose
This test file covers device-number conversion and Linux read-access behavior used by mount and metadata helpers.

## Important APIs, Types, and Functions
`TestDeviceNumber` validates `getDeviceNumber`, `DeviceNumber.String`, and `newDeviceNumberFromString`. `TestHaveReadAccessTo` checks `HaveReadAccessTo` against temporary file permission modes.

## Control Flow
The device test asserts `/NONEXISTENT` fails, `/dev/null` formats as `1:3`, and invalid strings fail to parse. The access test creates a temporary file, changes permissions, and compares `HaveReadAccessTo` with expected Linux owner-bit precedence.

## State and Persistence
State is limited to temporary files removed at test end. No repository files are modified.

## Dependencies and Integration Points
Uses `util.IsUserRoot` to skip access checks under root, because root bypasses normal permission behavior. Validates assumptions used by `filesystem` and `mountpoint`.

## Risks
The read-access test is Linux-specific and intentionally skipped as root. `/dev/null` major/minor assumptions are Linux-specific.

## Test Signals
Coverage confirms basic parsing/formatting and non-root permission semantics. It does not cover symlink canonicalization or umask override behavior.
