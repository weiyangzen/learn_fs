
# sources/sync-backup/kopia/tests/end_to_end_test/snapshot_gc_test.go

## Purpose
Tests that unreferenced snapshot content is collected only when maintenance safety permits it, across repository format versions.

## Important APIs, Types, And Functions
- `TestSnapshotGC` is a method on `formatSpecificTestSuite`, so it runs for format v1/v2/v3 via `suite_test.go`.
- Uses `content list`, `snap create`, `snap list -m`, `manifest rm`, `snapshot verify`, and `maintenance run --full` with `--safety=full` and `--safety=none`.

## Control Flow
The test records initial content count, creates a one-file snapshot, expects three new content items, removes snapshot manifests by parsing `snap list -m`, verifies snapshots, runs safe maintenance and checks content count remains unchanged, waits two seconds, then runs unsafe maintenance and expects two content items removed.

## State And Persistence Behavior
Manipulates content blobs, snapshot manifests, and maintenance-generated manifests. Safety mode and object age determine garbage collection eligibility.

## Dependencies And Integration Points
Uses `repo/content.Info`, `testutil.MustParseJSONLines`, `testenv`, and format-specific repository flags. Integrates manifest deletion, snapshot verification, content listing, and maintenance GC.

## Risks And Edge Cases
The test relies on content count deltas and a sleep to get past age boundaries. If content packing/indexing changes, exact counts may need adjustment. Manifest output parsing searches for `manifest:` in human output.

## Test Signals
Good signal for GC safety semantics and format-version compatibility.
