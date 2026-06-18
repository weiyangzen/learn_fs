# sources/sync-backup/syncthing/lib/versioner/simple.go

Purpose: simple count/age-based file versioner.

Important APIs and control flow: `init` registers factory `simple`. `newSimple` reads `keep` with default 5 and optional `cleanoutDays`, builds source and versions filesystems, and stores copy-range method. `Archive` moves the file to the versions filesystem using `archiveFile` with `TagFilename`, then calls `cleanVersions` for that file using `toRemove`. `GetVersions` and `Restore` delegate to shared retrieval/restore helpers. `Clean` runs global version cleanup. `toRemove` sorts version names, removes oldest entries beyond `keep`, then if `cleanoutDays > 0`, parses remaining timestamp tags and removes versions older than the max age.

State and persistence: moves files from folder filesystem into versions filesystem and deletes old version files.

Dependencies and integration: uses config versioning params, fs abstraction, shared versioner helpers, and local time parsing.

Risks: invalid timestamp tags are skipped for age cleanup. `keep <= 0` can remove all count-limited versions depending on slicing behavior. Tests cover count, tilde paths, permissions via shared helpers.
