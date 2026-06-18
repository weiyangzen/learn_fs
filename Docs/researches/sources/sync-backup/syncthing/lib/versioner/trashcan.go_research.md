# sources/sync-backup/syncthing/lib/versioner/trashcan.go

Purpose: trashcan-style versioner that moves deleted/changed files into a versions area without timestamping the archived filename.

Important APIs and control flow: `init` registers `trashcan`. `newTrashcan` reads optional `cleanoutDays`, builds folder and versions filesystems, and stores copy-range method. `Archive` calls `archiveFile` with an identity tagger, so archive paths match original paths. `Clean` returns immediately when cleanout is disabled or versions dir is missing; otherwise it computes a cutoff, walks the versions filesystem, records directories, removes files older than cutoff, marks directories containing retained files, and deletes empty directories afterward. `GetVersions` delegates retrieval. `Restore` handles the untagged archive collision case by temporarily tagging any existing destination file, restoring the requested version, then renaming the temporary archive back if needed.

State and persistence: moves files into versions filesystem, deletes old trashcan files, removes empty directories, and may temporarily rename archived destination conflicts.

Dependencies and integration: config, fs abstraction, `emptyDirTracker`, and shared archive/restore helpers.

Risks: restore collision logic is subtle because untagged archive names can be overwritten. Clean uses file modtime, not embedded tag time. No direct tests in this batch for trashcan restore/clean.
