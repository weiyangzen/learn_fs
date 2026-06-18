# sources/sync-backup/restic/internal/archiver/testing_test.go

Purpose: Tests the archiver test-helper utilities themselves.

Important APIs and types: `MockT` captures helper failures without aborting the outer test. `createFilesAt` creates flat test fixtures. Tests cover `TestCreateFiles`, `TestWalkFiles`, `TestEnsureFiles`, and `TestEnsureSnapshot`.

Control flow and state: The tests create local directory structures, compare observed item types and contents, intentionally pass mismatched expectations through `MockT`, and assert that helpers fail when they should. Snapshot helper tests create a repository, run a real archiver snapshot, and compare expected `TestDir` layouts.

Dependencies and integration: Uses `repository.TestRepository`, `New`, `Snapshot`, `internal/test`, `go-cmp`, `fs.NewLocal`, and temporary directories.

Risks and test signals: These tests protect the reliability of the larger archiver suite by confirming helpers detect missing, extra, wrong-content, wrong-type, wrong-symlink, and snapshot-tree mismatches.
