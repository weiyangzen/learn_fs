# sources/sync-backup/kopia/snapshot/snapshotfs/source_directories_test.go

Purpose: integration test for the virtual all-sources filesystem hierarchy.

Important APIs/types/functions: `TestAllSources`, `iterateAllNames`, and `mustWriteSnapshotManifest`.

Control flow: the test uploads one base manifest, rewrites copies of it with varied users, hosts, source paths, case differences, roots, and timestamps, then walks `snapshotfs.AllSourcesEntry` recursively and compares the exact set of directory names.

State and persistence: writes multiple snapshot manifests into a test repository. The same root entry is reused while source and start time are changed.

Dependencies and integration points: covers `AllSourcesEntry`, `sourceDirectories`, `sourceSnapshots`, safe-name disambiguation, manifest listing, and repository-backed directory entries.

Risks and test signals: expected names encode timestamp formatting and collision suffixing. The helper uses recursive `fs.IterateEntries`, so failures can come from iterator behavior as well as naming logic.
