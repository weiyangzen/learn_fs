# sources/sync-backup/kopia/tests/clitestutil/clitestutil.go

## Purpose
Provides parsing helpers for CLI end-to-end tests, primarily for `snapshot list -l --manifest-id` and `ls -l` output.

## Important APIs, Types, and Functions
`SourceInfo`, `SnapshotInfo`, and `DirEntry` are parsed representations. `MustParseSnapshots`, `mustParseSnapshotInfo`, `mustParseSourceInfo`, `ListSnapshotsAndExpectSuccess`, `ListDirectory`, and `ListDirectoryRecursive` are the main helpers. `testEnv` captures the `RunAndExpectSuccess` method needed from test environments.

## Control Flow
Snapshot parsing treats non-indented lines as `user@host:path` source headers and two-space-indented lines as snapshots. Snapshot lines are split by spaces, timestamp fields are joined and parsed, and manifest/object fields shift depending on whether the line contains `incomplete`. Directory parsing uses fixed fields from `ls -l`.

## State and Persistence Behavior
No persistent state; helpers fail tests directly through `testing.TB`.

## Dependencies and Integration Points
Used by many end-to-end tests in this subset for snapshot count, snapshot IDs, object IDs, and directory entry object IDs.

## Risks
Parsing is tightly coupled to CLI text column formats and timezone layout. Any display wording, spacing, or incomplete-marker change can break unrelated tests. `mustParseDirectoryEntries` assumes at least seven fields.

## Test Signals
Indirectly validated across ACL, all-format, compression, diff, ECC, index recovery, restore, repository sync, and checkpoint tests.
