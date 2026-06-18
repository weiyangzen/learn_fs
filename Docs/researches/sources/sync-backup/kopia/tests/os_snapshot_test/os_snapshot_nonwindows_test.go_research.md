
# sources/sync-backup/kopia/tests/os_snapshot_test/os_snapshot_nonwindows_test.go

## Purpose
Defines the non-Windows side of the `os_snapshot_test` package with a build tag excluding Windows.

## Important APIs, Types, And Functions
No runtime code beyond package declaration.

## Control Flow
The `//go:build !windows` tag ensures this file participates on non-Windows platforms so the package exists even though Windows-specific shadow-copy tests are excluded.

## State And Persistence Behavior
No state or persistence.

## Dependencies And Integration Points
Serves build-system/package compatibility for `tests/os_snapshot_test`.

## Risks And Edge Cases
If additional non-Windows tests are expected, this file currently provides no assertions.

## Test Signals
No behavioral test signal; build/package placeholder only.
