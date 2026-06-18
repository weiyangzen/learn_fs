## sources/sync-backup/kopia/fs/localfs/local_fs_os.go

Purpose: implements OS directory iteration, child lookup, entry classification, and path-to-entry conversion.

Important APIs/types/functions: `filesystemDirectoryIterator`, `Iterate`, `Child`, `toDirEntryOrNil`, `NewEntry`, `entryFromDirEntry`, and `newEntry`.

Control flow, state, and persistence: directory iterators keep an open `os.File` handle and read `numEntriesToRead` directory entries at a time. For each name, `os.Lstat` decides whether to return a file, directory, symlink, shallow placeholder, or error entry. Permission-denied child `Lstat` failures become `fs.ErrorEntry` instances instead of aborting the directory. `NewEntry` cleans paths and has a Windows retry for direct volume paths that require a trailing separator.

Dependencies and integration points: integrates OS metadata with `fs` interfaces, shallow placeholder detection, and platform-specific metadata functions. `fs.IterateEntries` callers depend on `Close` to release directory handles.

Risks and test signals: risks include leaking directory handles if iterators are not closed, platform-specific path quirks, and inconsistent behavior between `ReadDir` and `Lstat`. Tests cover non-existent iteration, large/small iteration counts, child lookup, local path normalization, split paths, and permission-denied entries.
