# sources/sync-backup/syncthing/lib/protocol/nativemodel_windows_test.go

## Purpose
Unit test for Windows path fixup behavior in `nativemodel_windows.go`.

## Important APIs, Types, and Functions
`TestFixupFiles` constructs `[]FileInfo`, calls `fixupFiles`, and compares with `reflect.DeepEqual`.

## Control Flow
The test passes five entries: a normal slash path, an invalid backslash path, a deleted invalid backslash path, a simple file name, and another slash path. It expects three output entries with slash paths converted to backslash paths and invalid entries removed.

## State and Persistence Behavior
No persistent state. The test validates in-memory slice filtering and conversion semantics.

## Dependencies and Integration Points
Depends on `reflect` and Windows-only implementation symbols. It is intended for Windows builds where `fixupFiles` exists.

## Risks and Edge Cases
The test focuses on filtering and conversion but does not assert logging severity or request rejection. It also does not test the no-invalid fast path where the original slice is returned.

## Test Signals
A passing test confirms invalid backslash-containing index entries are not passed through and normal slash-separated names are converted to native Windows separators.
