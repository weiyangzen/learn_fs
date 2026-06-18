## sources/sync-backup/kopia/fs/localfs/shallow_fs.go

Purpose: implements shallow restore placeholders that store `snapshot.DirEntry` metadata on disk without materializing original file or directory contents.

Important APIs/types/functions: `WriteShallowPlaceholder`, `placeholderPath`, `dirEntryFromPlaceholder`, `checkedDirEntryFromPlaceholder`, `shallowFilesystemFile`, `shallowFilesystemDirectory`, and their `DirEntryOrNil` methods.

Control flow, state, and persistence: `WriteShallowPlaceholder` JSON-encodes a `snapshot.DirEntry` and writes it atomically to a file path with `.kopia-entry` suffix; directory placeholders are represented as a directory containing a nested `.kopia-entry` file. Reading verifies the real path does not also exist, preventing ambiguous/corrupt shallow trees. Shallow files cannot be opened, and shallow directories cannot be iterated or child-looked-up.

Dependencies and integration points: uses `internal/atomicfile`, `ospath.SafeLongFilename`, and `snapshot.HasDirEntryOrNil`. `entryFromDirEntry` detects the suffix and creates shallow wrappers.

Risks and test signals: risks include interrupted restores leaving both placeholder and real paths, JSON schema drift, and unsupported operations surfacing during traversal. Tests are indirect through localfs and restore behavior elsewhere.
