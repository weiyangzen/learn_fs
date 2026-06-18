# sources/sync-backup/kopia/snapshot/snapshotfs/dir_manifest_builder.go

Purpose: concurrent builder for serialized directory manifests and recursive directory summaries.

Important APIs/types/functions: `DirManifestBuilder`, `Clone`, `AddEntry`, `AddFailedEntry`, `Build`, `isDir`, and `sortedTopFailures`.

Control flow: `AddEntry` appends a `snapshot.DirEntry` and updates aggregate summary counts, sizes, max mod time, and child failure summaries. `AddFailedEntry` records ignored or fatal errors. `Build` increments total directory count, sets max mod time for empty directories, stores incomplete reason, trims/sorts failures, sorts entries with directories first, and returns a `snapshot.DirManifest`.

State and persistence: state is mutex-protected in memory. Persistence happens later through `WriteDirManifest`.

Dependencies and integration points: used by upload checkpointing, directory rewrite, and directory writer paths.

Risks and test signals: `Build` mutates internal entry order and failure list; callers should not assume stable insertion order. Symlink file sizes are not propagated into total file size. Tests cover files, symlinks, and directory child summaries.
