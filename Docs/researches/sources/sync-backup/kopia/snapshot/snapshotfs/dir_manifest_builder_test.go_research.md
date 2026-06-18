# sources/sync-backup/kopia/snapshot/snapshotfs/dir_manifest_builder_test.go

Purpose: unit coverage for `DirManifestBuilder.AddEntry` summary aggregation.

Important APIs/types/functions: `TestAddEntry`, `DirManifestBuilder`, `snapshot.DirEntry`, and `fs.DirectorySummary`.

Control flow: three subcases add a file, a symlink, and a directory with a child summary, then assert the builder summary counters and max modification time.

State and persistence: only in-memory builder state is inspected; no directory manifest is written to the repository.

Dependencies and integration points: validates summary fields consumed by repository-backed directory entries, storage stats, restore progress, and UI display.

Risks and test signals: the symlink case intentionally skips total-size checking because symlink size is not propagated. The test does not cover `Build` sorting, failed-entry trimming, or concurrent `AddEntry`, so those rely on other coverage or code review.
