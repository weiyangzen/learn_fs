<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errors_unix_test.go -->
# sources/storage-engines/pebble/vfs/errors_unix_test.go

## Purpose
Tests Unix no-space error classification.

## Important APIs, Types, and Functions
`TestIsNoSpaceError` wraps `unix.ENOSPC` with CockroachDB stack context and asserts `IsNoSpaceError` returns true.

## Control Flow
The test constructs one wrapped errno and checks it through `require.True`.

## State and Persistence Behavior
No filesystem state is created; the test is purely error-classification logic.

## Dependencies and Integration Points
Covers `errors_unix.go` and relies on `errors.WithStack` preserving `errors.Is` matching. Built on the same Unix-like platforms as the implementation.

## Risks and Edge Cases
The test only covers the positive `ENOSPC` case, not false positives or related errors like quota exhaustion.

## Test Signals
Passing confirms wrapped errno matching remains compatible with the VFS helper.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/vfs/errors_unix_test.go -->
