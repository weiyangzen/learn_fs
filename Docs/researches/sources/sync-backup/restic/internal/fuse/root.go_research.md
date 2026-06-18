## sources/sync-backup/restic/internal/fuse/root.go

Purpose: root object for a restic repository FUSE mount and top-level configuration.

Important APIs/types: `Config` controls ownership display, snapshot filtering, time formatting, and path templates. `Root` holds the repository, config, 64 MiB blob LRU cache, embedded `SnapshotsDir`, and mount UID/GID. `NewRoot` initializes cache, ownership defaults, path-template defaults (`ids/%i`, `snapshots/%T`, `hosts/%h/%T`, `tags/%t/%T`), and the root `SnapshotsDir`. `Root()` satisfies `fs.FS`.

Control flow and state: `NewRoot` copies the input config into `root.cfg`, but default path templates are assigned to the local `cfg` before building `SnapshotsDirStructure`; consumers should not expect `root.cfg.PathTemplates` to reflect those defaults. UID/GID default to current process owner unless `OwnerIsRoot` leaves zero values.

Dependencies and integration points: integrates `restic.Repository`, `bloblru`, `data.SnapshotFilter`, `debug`, and `anacrolix/fuse/fs`. The embedded `SnapshotsDir` handles directory listing and lookup for root paths.

Risks and test signals: root ownership and path-template defaults shape the visible mount. `TestTopUIDGID` validates owner behavior for top-level directories. Blob cache sizing is hard-coded and noted as TODO, so memory-sensitive deployments have no local control here.
