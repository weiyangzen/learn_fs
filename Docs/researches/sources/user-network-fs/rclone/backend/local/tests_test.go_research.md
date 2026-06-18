
# sources/user-network-fs/rclone/backend/local/tests_test.go

## Purpose
Tests Windows path cleaning and encoding behavior.

## Important APIs, Types, And Control Flow
`testsWindows` contains raw input/output path pairs covering drive paths, long UNC paths, slash normalization, and replacement of Windows-reserved characters. `TestCleanWindows` skips non-Windows platforms and asserts `cleanRootPath(..., true, encoder.OS)` matches each expected path.

## State And Persistence
No filesystem changes are made; the test checks string transformation only.

## Dependencies And Integration Points
Directly validates local `cleanRootPath`, Windows path normalization, and `encoder.OS`.

## Risks And Test Signals
Signals regressions in root path encoding before filesystem operations. It does not test `noUNC=false` conversion or actual filesystem access.
