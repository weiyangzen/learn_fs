# sources/sync-backup/kopia/snapshot/restore/restore.go

Purpose: central restore engine that walks an `fs.Entry` snapshot tree and writes it to any `Output` implementation, including filesystem, tar, zip, or shallow filesystem output.

Important APIs/types/functions: `Output`, `Stats`, `Options`, `Entry`, internal `copier`, `copyEntry`, `copyEntryInternal`, `copyDirectory`, `deleteExtraFilesInDir`, and `copyDirectoryContent`.

Control flow: `Entry` builds a parallelwork queue, enqueues the root, chooses worker count from options/CPU/output serializability, processes work, closes output, and returns atomic stats. Directories are enqueued to the front, files to the back. Incremental mode skips matching existing files/symlinks. Delete-extra prunes local filesystem entries absent from the snapshot.

State and persistence: maintains atomic restore counters and may create, overwrite, skip, or delete target data through the output. Cancellation returns through completion callbacks rather than abruptly killing queued state.

Dependencies and integration points: relies on `fs.GetAllEntries`, `parallelwork.Queue`, `FilesystemOutput`, and shallow output wrapping.

Risks and test signals: delete-extra is filesystem-only and destructive when enabled. Error ignoring increments counters and suppresses failures. Depth-based shallow behavior depends on `RestoreDirEntryAtDepth` and placeholder suffix safety.
