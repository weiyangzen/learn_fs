# sources/sync-backup/kopia/snapshot/snapshotfs/source_directories.go

Purpose: virtual directory level that groups snapshots for one `user@host` by source path using filesystem-safe names.

Important APIs/types/functions: `sourceDirectories`, `Iterate`, `disambiguateSafeNames`, and `safeNameForMount`.

Control flow: `Iterate` lists all sources, filters to the configured `userHost`, maps original paths to safe names, disambiguates case-insensitive collisions recursively, and returns `sourceSnapshots` entries. `safeNameForMount` normalizes root, Windows drive prefixes, forward/back slashes, trailing underscores, and trailing colons.

State and persistence: read-only synthetic directory state; modification time comes from repository time.

Dependencies and integration points: child of `repositoryAllSources` and parent of timestamped snapshot directories for mount/browse features.

Risks and test signals: name disambiguation must be deterministic and collision-safe on case-sensitive and case-insensitive filesystems. Internal tests cover path normalization and recursive collision resolution; source tree tests cover full mount names.
