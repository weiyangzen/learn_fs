# sources/sync-backup/kopia/snapshot/snapshotfs/snapshot_storage_stats_test.go

Purpose: validates `CalculateStorageStats` for duplicate content, repeated snapshots, and incremental additions.

Important APIs/types/functions: `TestCalculateStorageStats`, `mockfs`, `repotesting`, `upload.NewUploader`, and `snapshotfs.CalculateStorageStats`.

Control flow: the test uploads a directory with two unique file contents and one duplicate, uploads the same tree again, adds one new file, uploads a third snapshot, computes stats for all three, and compares exact `StorageStats` structs.

State and persistence: writes snapshot objects and manifests to a test repository and flushes between uploads. Stats are collected from callback-mutated manifests.

Dependencies and integration points: covers uploader, repository object/content accounting, tree walker dedupe, and packed/original content sizes.

Risks and test signals: expected packed byte counts are format/implementation-sensitive. The key behavioral signals are nonzero first snapshot, all-zero new data for identical second snapshot, and only changed root/dir/file content for the third.
