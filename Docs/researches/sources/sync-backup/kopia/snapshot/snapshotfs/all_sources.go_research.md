# sources/sync-backup/kopia/snapshot/snapshotfs/all_sources.go

Purpose: exposes a virtual read-only root directory containing all snapshot sources in a repository grouped by user and host.

Important APIs/types/functions: `repositoryAllSources`, its `fs.Directory` methods, `Iterate`, and `AllSourcesEntry`.

Control flow: `Iterate` lists all source infos, deduplicates `username@host`, converts each to a filesystem-safe name via `safeNameForMount`, disambiguates case-insensitive collisions, and returns `sourceDirectories` children.

State and persistence: no repository writes. Directory metadata is synthetic, with modification time from `rep.Time()` and read-only directory mode.

Dependencies and integration points: used by browse/mount features that present repository snapshots as a filesystem. Depends on `snapshot.ListSources`, `fs.StaticIterator`, and source directory helpers.

Risks and test signals: source names with slashes, backslashes, or case collisions need deterministic disambiguation. Tests under `source_directories_test.go` validate expected tree names for mixed source paths and usernames.
