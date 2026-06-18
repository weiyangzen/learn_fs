# sources/sync-backup/restic/internal/fs/fs_local_test.go

Purpose: Cross-platform tests for local `FS` metadata and readable transitions.

Important APIs: `TestFSLocalMetadata`, `TestFSLocalRead`, `TestFSLocalReaddir`, `TestFSLocalReadableRace`, and `TestFSLocalTypeChange`.

Control flow and state: Table-driven setup creates files, directories, symlinks, and symlink targets. Tests open metadata-only and normal files, call `MakeReadable`, compare `ExtendedFileInfo` to `os.Stat`/`os.Lstat`, and convert to `data.Node`.

Dependencies and integration: Validates `NewLocal`, `localFile.cacheFI`, `ToNode`, `O_NOFOLLOW`, and directory reads.

Risks: Race/type-change tests intentionally accept both handle-based and path-based implementations, so they document rather than forbid TOCTOU behavior.

Test signals: Strong coverage for the main local filesystem abstraction used by backup traversal.
