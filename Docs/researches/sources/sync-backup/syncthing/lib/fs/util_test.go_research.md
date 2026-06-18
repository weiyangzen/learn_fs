# sources/sync-backup/syncthing/lib/fs/util_test.go

## Purpose
Tests utility helpers for common path prefixes, Windows filename validation, and path sanitization.

## Important APIs, Types, and Functions
`TestCommonPrefix`, `TestWindowsInvalidFilename`, `TestSanitizePath`, `TestSanitizePathFuzz`, `BenchmarkWindowsInvalidFilenameValid`, and `BenchmarkWindowsInvalidFilenameNUL`.

## Control Flow
Table tests branch on Windows vs Unix expected separators and volume semantics. Filename tests check reserved names, reserved characters, and trailing-space/period rules. Sanitization tests compare exact outputs and fuzz random bytes to ensure valid printable UTF-8.

## State and Persistence Behavior
No persistent state.

## Dependencies and Integration Points
Covers `CommonPrefix`, `WindowsInvalidFilename`, `SanitizePath`, and error wrapping with sentinel invalid filename errors.

## Risks
Platform conditionals mean some cases only run on Windows. Fuzz loop uses random bytes but fixed count, giving smoke coverage rather than exhaustive fuzzing.

## Test Signals
Good regression coverage for path safety helpers used throughout filesystem setup and UI-facing path generation.
