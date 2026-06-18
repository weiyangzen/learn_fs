# sources/sync-backup/restic/internal/fs/fs_local.go

Purpose: Implements the `FS` and `File` interfaces for the host filesystem.

Important APIs: `NewLocal`, methods on `local`, `newLocalFile`, `localFile.MakeReadable`, `Stat`, `ToNode`, `Read`, `Readdirnames`, and `Close`.

Control flow and state: Package init attempts to enable platform privileges. `newLocalFile` either opens the file immediately or returns a metadata-only object. `cacheFI` lazily caches metadata using the open file handle, `Lstat`, or `Stat` depending on follow flags. `MakeReadable` reopens a metadata-only file and resets cached metadata.

Dependencies and integration: Bridges OS files to backup logic via `ExtendedFileInfo` and `nodeFromFileInfo`. Used directly for normal backup/restore and wrapped by `LocalVss` and `Track`.

Risks: Metadata-only mode may be path-based on local filesystems, so race behavior after rename/type changes is implementation-dependent and explicitly tolerated by tests. `Read`/`Readdirnames` assume `MakeReadable` or non-metadata open has supplied `f.f`.

Test signals: `fs_local_test.go` covers metadata, symlink following, file reads, directory reads, race after rename, and type changes.
