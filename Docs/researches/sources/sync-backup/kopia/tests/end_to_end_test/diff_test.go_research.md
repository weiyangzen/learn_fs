# sources/sync-backup/kopia/tests/end_to_end_test/diff_test.go

## Purpose
End-to-end smoke test for `diff` across every pair of snapshots from a changing directory.

## Important APIs, Types, and Functions
`TestDiff` uses CLI repo/snapshot/diff commands and `clitestutil.ListSnapshotsAndExpectSuccess`.

## Control Flow
The test snapshots an empty directory, adds directories and files, snapshots again, modifies one file and adds another directory, snapshots, deletes a file, snapshots, then runs `diff -f` for every ordered pair of snapshot root object IDs.

## State and Persistence Behavior
Persists four snapshots for one source path and exercises file add/modify/delete state across roots.

## Dependencies and Integration Points
Covers snapshot upload, snapshot listing, object-root addressing, and diff output generation.

## Risks
The test asserts only command success, not diff content. It can miss semantic regressions that still exit zero.

## Test Signals
Any crash or error in pairwise diffing across empty, added, modified, and deleted tree states fails the test.
