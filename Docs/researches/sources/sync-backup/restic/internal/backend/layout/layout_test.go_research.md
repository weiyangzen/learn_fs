<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/layout/layout_test.go -->
# sources/sync-backup/restic/internal/backend/layout/layout_test.go

## Purpose
Verifies DefaultLayout and RESTLayout path mapping, directory lists, Basedir behavior, and layout names.

## Important APIs, Types, And Functions
TestDefaultLayout and TestRESTLayout are the core tests with table-driven cases.

## Control Flow
The tests build layouts with filepath.Join or path.Join, compare filenames, sort Paths output where necessary, and validate pack subdirectory behavior.

## State And Persistence Behavior
No persistent state except temporary directories allocated by the test helper.

## Dependencies And Integration Points
Depends on filepath/path, reflect/sort/testing, internal/backend, and internal/test.

## Risks And Edge Cases
The tests focus on known file types and path expectations; invalid handle/file-type behavior remains a caller contract.

## Test Signals
Strong unit signal for source-tree path layout invariants used by several backends.
<!-- END_FILE_RESEARCH: sources/sync-backup/restic/internal/backend/layout/layout_test.go -->
