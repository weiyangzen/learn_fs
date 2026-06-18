# sources/user-network-fs/gcsfuse/internal/fs/local_file_test.go

Purpose: integration-style tests for newly created local files when `Write.CreateEmptyFile` is disabled. The suite verifies that local writes remain unsynced until close or sync, interact correctly with directory listings and local deletion, and eventually persist to GCS only when the filesystem semantics require it.

Important APIs/helpers: `LocalFileTest` embeds `fsTest` and testify suite. `SetupSuite` enables implicit directories and disables empty-file creation. Helpers create local files with `os.OpenFile(...O_CREATE|O_TRUNC|O_DIRECT)`, assert the GCS object is absent, validate directory entries, close files, and compare bucket contents via `storageutil.ReadObject` and `bucket.StatObject`.

Control flow and state: tests create files under root, explicit dirs, and implicit dirs, write/truncate/random-write data, and assert no GCS object exists before close. ReadDir and WalkDir tests check that unsynced local files appear in listings alongside GCS-backed entries. Rename and rmdir tests distinguish local-file constraints: renaming a local file persists it under the new name, renaming a directory containing an unsynced local file fails until the file is synced, and removing directories containing local files unlinks them without uploading.

Persistence behavior: close uploads dirty local files unless they were unlinked. `Sync` on an unlinked local file is a no-op for GCS. Deleting a synced local file removes the object. Symlink tests show symlinks can target local unsynced files and become dangling after the local target is removed.

Dependencies and integration: uses mounted filesystem operations, fake bucket state, `storageutil`, `inode.ConflictingFileNameSuffix`, fusetesting time extraction, metrics/tracing config, and implicit-directory behavior.

Risks: some tests rely on entry ordering. `TestStatFailsOnNewFileAfterDeletion` mutates server config inside the test, which can be surprising in a shared suite. Local-vs-GCS state transitions are sensitive to open file handles and kernel writeback.

Test signals: strong coverage for delayed object creation, local listing visibility, unlink/rmdir safety, close-time persistence, timestamps, same-name recreation, and local symlink behavior.
