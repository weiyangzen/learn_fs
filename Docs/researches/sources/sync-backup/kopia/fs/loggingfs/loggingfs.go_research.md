## sources/sync-backup/kopia/fs/loggingfs/loggingfs.go

Purpose: provides a filesystem wrapper that logs timing and results for child lookup and directory reads.

Important APIs/types/functions: `Wrap`, `Option`, `Output`, `Prefix`, `loggingDirectory`, `loggingFile`, `loggingSymlink`, and `wrapWithOptions`.

Control flow, state, and persistence: wrapping preserves the underlying entry type when it is a directory, file, or symlink. `Child` times the underlying lookup and wraps the returned entry. `IterateEntries` materializes all entries with `fs.GetAllEntries`, logs count and duration, then invokes the caller callback. No persistence; state is limited to output callback and prefix.

Dependencies and integration points: uses `fs` abstractions and `internal/timetrack`. It is a diagnostic layer and can be inserted around any filesystem entry tree.

Risks and test signals: `applyOptions` defaults `printf` to the caller argument; passing nil without `Output` will panic on first log. Directory iteration changes streaming behavior by collecting all entries first. No dedicated tests in this subset.
