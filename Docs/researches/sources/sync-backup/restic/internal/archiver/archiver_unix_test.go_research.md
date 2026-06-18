# sources/sync-backup/restic/internal/archiver/archiver_unix_test.go

Purpose: Unix-only regression coverage for hardlink metadata in snapshots. It verifies that hardlinked files can retain device ID, inode, and link count metadata when the `DeviceIDForHardlinks` feature flag is enabled.

Important APIs and functions: `statAndSnapshot` compares metadata from `nodeFromFile` against a node saved through `snapshot`; `TestHardlinkMetadata` builds a source tree containing regular files, a hardlink, and a directory.

Control flow and state: The test enables the feature flag, creates files, snapshots `testlink`, `testfile`, and `testdir`, then compares metadata fields on returned `data.Node` values. Hardlink nodes should preserve device/inode/link count, while ordinary files and directories should have `DeviceID` zeroed.

Dependencies and integration: It depends on Unix hardlink support, `feature.TestSetFlag`, `fs.NewLocal`, the helpers in `archiver_test.go`, and the test repository created by `prepareTempdirRepoSrc`.

Risks and test signals: The file guards against leaking device IDs for ordinary nodes while still preserving the metadata necessary to identify hardlinks. It is excluded from Windows via build tag.
