# sources/sync-backup/restic/cmd/restic/cmd_list.go

Purpose: implements `restic list`, printing repository object IDs for `blobs`, `packs`, `index`, `snapshots`, `keys`, or `locks`.

Important APIs/types/functions: `newListCommand`; `runList`; cobra `ValidArgs` and exact-arg validation.

Control flow and state: `runList` checks one type argument, opens the repository with a read lock except lock listing can bypass locks, maps the type string to a `restic.FileType`, then lists IDs. For `blobs`, it iterates `repository.AllIndexBlobs` and prints blob type plus blob ID from the loaded indexes; for other types it calls `repo.List`.

Dependencies and integration points: depends on repository index functions, restic file-type constants, cobra argument validation, and terminal printer. It is used heavily by integration tests to discover snapshots/packs.

Risks: `list blobs` output shape differs from other types, which consumers must handle. Blob listing depends on a usable index and can surface index errors.

Test signals: list integration tests compare `list blobs` output against `repo.ListBlobs` after a backup.
