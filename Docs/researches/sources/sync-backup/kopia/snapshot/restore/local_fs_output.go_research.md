# sources/sync-backup/kopia/snapshot/restore/local_fs_output.go

Purpose: implements `restore.Output` for writing a snapshot tree to the local filesystem with overwrite, ownership, permissions, timestamp, sparse, atomic, flush, and shallow-placeholder cleanup options.

Important APIs/types/functions: `FilesystemOutput`, `Init`, `BeginDirectory`, `FinishDirectory`, `WriteFile`, `FileExists`, `CreateSymlink`, `SymlinkExists`, `setAttributes`, `createDirectory`, `copyFileContent`, `write`, `getStreamCopier`, and `progressReportingReader`.

Control flow: initialization chooses sparse or regular copy. Directories are created before traversal and attributed after children. Files are opened from the snapshot, copied to a safe long filename, optionally via `atomicfile.Write`, then attributed. Symlinks are overwritten only when allowed and use OS-specific lchown/chmod/chtimes helpers.

State and persistence: writes real files, directories, symlinks, permissions, owners, mtimes, and optionally fsyncs file data. It removes shallow placeholder sidecars after writing real entries.

Dependencies and integration points: used by `restore.Entry`; depends on `localfs`, `atomicfile`, `ospath`, `sparsefile`, `stat`, and platform symlink helpers.

Risks and test signals: overwrite and delete-extra behavior can remove local data when enabled. Atomic writes do not use sparse copy. Permission failures may be ignored by option. Existing-file skip uses size and mtime tolerance.
