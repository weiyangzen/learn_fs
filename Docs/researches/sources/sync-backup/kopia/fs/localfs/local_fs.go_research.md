## sources/sync-backup/kopia/fs/localfs/local_fs.go

Purpose: defines core local filesystem entry types and public constructors for turning OS paths into Kopia `fs.Entry` and `fs.Directory` objects.

Important APIs/types/functions: `filesystemEntry`, `filesystemDirectory`, `filesystemFile`, `filesystemSymlink`, `filesystemErrorEntry`, `Directory`, `NewEntry`, `splitDirPrefix`, `fileWithMetadata.Entry`, `Open`, `Readlink`, and `Resolve`.

Control flow, state, and persistence: entries store name, size, mode, nanosecond mtime, owner/device info, and a prefix used to reconstruct the local path. `Directory` calls `NewEntry` and accepts real directories plus symlinks that may behave like directories, which supports Windows VSS edge cases. `filesystemFile.Open` opens the current OS path and returns a reader that can report updated metadata. There is no internal persistence; state mirrors OS metadata captured at entry creation.

Dependencies and integration points: uses `os`, `filepath`, platform-specific metadata helpers, and Kopia `fs` interfaces. `Resolve` uses `filepath.EvalSymlinks`, so returned paths are canonicalized by the OS.

Risks and test signals: risks include stale metadata, symlink resolution differences, path splitting on Windows/Unix, and object pooling interactions in companion files. Tests cover symlinks, file/directory enumeration, child lookup, root path handling, and split prefix cases.
