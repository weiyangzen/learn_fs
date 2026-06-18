# sources/sync-backup/syncthing/lib/fs/filesystem_test.go

## Purpose
Tests shared filesystem helpers and a wrapper-ordering regression involving case conflict detection and mtime virtualization.

## Important APIs, Types, and Functions
`TestIsInternal`, `TestCanonicalize`, `TestFileModeString`, `TestIsParent`, and `TestRepro9677MissingMtimeFS`.

## Control Flow
Table tests validate internal `.stfolder`, `.stignore`, `.stversions` handling; canonical path acceptance/rejection; parent path logic across relative/absolute paths; and mode string formatting. The regression test creates an mtime-enabled case-detecting fake FS, resets the global case registry, creates a case FS without mtime, then verifies a later mtime-enabled FS still preserves virtual mtimes.

## State and Persistence Behavior
Uses fakeFS and a map-backed mtime database. Mutates `globalCaseFilesystemRegistry` in the regression test.

## Dependencies and Integration Points
Covers `NewFilesystem` wrapper order, `OptionDetectCaseConflicts`, `NewMtimeOption`, `UnicodeLowercaseNormalized`, and platform path differences.

## Risks
Path semantics vary by Windows vs Unix and are branch-tested. The regression test intentionally touches global state, so isolation matters.

## Test Signals
High-value safety coverage for root traversal prevention, internal-file ignoring, and wrapper cache correctness.
