## sources/sync-backup/restic/internal/fuse/snapshots_dirstruct.go

Purpose: constructs and refreshes the pseudo directory tree that maps snapshot metadata to user-facing paths such as IDs, timestamps, hosts, users, and tags.

Important APIs/types: `MetaDirData` represents either a pseudo directory (`names`), a snapshot mount point (`snapshot`), or a symlink (`linkTarget`). `SnapshotsDirStructure` stores root/config, a mutex-protected `entries` map, last snapshot hash, and reload timestamp. `pathsFromSn` expands `%T`, `%t`, `%i`, `%I`, `%u`, `%h` templates. `filenameFromTag`, `staticPrefix`, and `uniqueName` sanitize and stabilize generated paths. `makeDirs` builds entries, intermediate directories, static prefixes, mount points, and `latest` links. `updateSnapshots` reloads snapshots, sorts them by time and ID, hashes IDs to detect changes, loads repository index on change, and rebuilds entries. `UpdatePrefix` returns one metadata node for a prefix.

Control flow and state: reloads are throttled by `minSnapshotsReloadTime` (60 seconds). Snapshot IDs are hashed after deterministic sorting; if the hash is unchanged only `lastCheck` is updated. `makeDirs` uses a recursive `mount` closure to populate child pointers and parent directories. Latest links are updated when a snapshot time is not before the recorded latest, so equal timestamps prefer later sorted snapshots.

Dependencies and integration points: depends on `data.SnapshotFilter.FindAll`, `restic.Repository.LoadIndex`, `data.Snapshots`, SHA-256, and FUSE directory consumers. Template expansion directly defines the visible mount tree consumed by `SnapshotsDir`.

Risks and test signals: templates containing path separators in host/user/tag values can shape nested paths; tags are sanitized, but host and username replacements are not sanitized here. Snapshot changes that do not alter IDs do not rebuild metadata. Tests heavily cover template expansion, duplicate timestamp suffixes, latest-link targets, empty static directories, tag filename sanitization, and internal tree integrity.
