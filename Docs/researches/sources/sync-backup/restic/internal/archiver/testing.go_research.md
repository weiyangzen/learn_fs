# sources/sync-backup/restic/internal/archiver/testing.go

Purpose: Shared test helper library for archiver package tests. It creates synthetic filesystem trees, snapshots them, and validates repository or local filesystem contents against declarative `TestDir` structures.

Important APIs and types: `TestSnapshot`, `TestDir`, `TestFile`, `TestSymlink`, `TestHardlink`, `TestCreateFiles`, `TestWalkFiles`, `TestEnsureFiles`, `TestEnsureFileContent`, `TestEnsureTree`, and `TestEnsureSnapshot` are exported test helpers.

Control flow and state: `TestCreateFiles` sorts names so hardlink targets exist before hardlinks, then recursively creates files, symlinks, hardlinks, and directories. `TestEnsureFiles` walks expected and actual filesystem trees to catch missing, wrong-type, wrong-content, wrong-target, and extra paths. Repository validation loads snapshot and tree blobs, walks nodes, and for file content reconstructs data by loading each content blob into a buffer.

Persistence and dependencies: It writes temporary filesystem content and reads repository blobs. Dependencies include `data.LoadSnapshot`, `data.LoadTree`, `restic.BlobLoader`, `fs`, `debug`, and `internal/test` assertions.

Integration points: This file underpins nearly every archiver test and encodes the expected mapping from local files to restic tree nodes.

Risks and test signals: Helper bugs can mask archiver regressions, especially around path normalization, Windows symlink handling, and exact tree comparison. `testing_test.go` validates helper failure and success behavior.
