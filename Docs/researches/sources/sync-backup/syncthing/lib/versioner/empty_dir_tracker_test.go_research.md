# sources/sync-backup/syncthing/lib/versioner/empty_dir_tracker_test.go

Purpose: verifies empty-directory candidate tracking and removal order.

Important tests: `TestEmptyDirs` models a `.stversions` tree with two kept branches containing files and two empty remove branches. It adds dirs/files to `emptyDirTracker`, normalizes paths for Windows, and expects only empty branches returned deepest-first.

State and persistence: in-memory path list only.

Dependencies and integration: uses `messagediff` for readable diffs.

Risks and signals: good coverage for the tracker algorithm. It does not call `deleteEmptyDirs` against a filesystem or cover removal errors.
