<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/foreign_modifications_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/fs/foreign_modifications_test.go

Purpose: integration-tests read-only and externally modified GCS object scenarios, proving how the mounted filesystem observes remote object creation, overwrite, metadata changes, deletion, mtime metadata, symlinks, unreachable objects, and file/directory name conflicts.

Important APIs/types/functions: helper `setSymlinkTarget`; suite `ForeignModsTest`; tests `StatRoot`, `ReadDir_EmptyRoot`, `ReadDir_ContentsInRoot`, `ReadDir_EmptySubDirectory`, `ReadDir_ContentsInSubDirectory`, `UnreachableObjects`, `FileAndDirectoryWithConflictingName`, `SymlinkAndDirectoryWithConflictingName`, `StatTrailingNewlineName_NoConflictingNames`, `Inodes`, `OpenNonExistentFile`, `ReadFromFile_Small`, `ReadFromFile_Large`, `ReadBeyondEndOfFile`, overwrite/delete/metadata cases for files and directories, `Mtime`, `RemoteMtimeChange`, and `Symlink`.

Control flow: tests seed fake bucket contents out of band, then read/stat/open through the mounted filesystem. Conflict tests create both `foo` and `foo/` and assert directory wins the natural name while the file or symlink is exposed with `inode.ConflictingFileNameSuffix`. Overwrite/delete tests keep old file handles open, mutate the bucket remotely, and verify old handles still see old data or link count zero while new opens see new state or ENOENT.

State and persistence: fake bucket state is mutated directly outside the filesystem, while live inode/file-handle state remains in the mounted filesystem. Large-read testing repeatedly recreates a 4 MiB object and validates random ranges for about two seconds.

Dependencies and integration points: depends on `storageutil`, fake GCS bucket APIs, `inode` symlink metadata constants, `fusetesting`, Unix `syscall.Stat_t`, and `fsTest`. It validates generation-backed inode replacement and stale-handle semantics in `fs.go`.

Risks: time-bounded randomized large-read testing can be slow or variable. Error and stat details are Unix/FUSE-specific. Tests without implicit directories expect unreachable objects under missing placeholders.

Test signals: high-value coverage for consistency under remote modification, conflict-name exposure, mtime metadata parsing, symlink metadata handling, distinct inode IDs, EOF semantics, and stale open-handle behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/foreign_modifications_test.go -->
