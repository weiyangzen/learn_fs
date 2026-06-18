<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_persister_light.go -->
# sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_persister_light.go

This file implements a lighter key/value `robustness.Persister` using the in-process `tests/tools/kopiaclient.KopiaClient`. `KopiaPersisterLight` owns a Kopia client, a per-key in-process lock map, a condition variable, and a local base directory.

`ConnectOrCreateRepo` and `SetCacheLimits` use filesystem or S3 storage depending on `S3BucketNameEnvKey`. `Store`, `Load`, and `Delete` serialize access per key with `waitFor`/`doneWith`, then call `SnapshotCreate`, `SnapshotRestore`, or `SnapshotDelete`. Whole-metadata lifecycle methods are no-ops; `GetPersistDir` returns the temp persistence root and `Cleanup` removes it.

State persists as one or more Kopia snapshot manifests per metadata key. The condition variable prevents concurrent writes/deletes/loads for the same key but allows different keys concurrently. Risks include no context cancellation while waiting, `Signal` waking only one waiter, cleanup not closing a repo handle because handles are opened per operation, and S3 env reliance. Tests cover light persister behavior.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/tests/robustness/snapmeta/kopia_persister_light.go -->
