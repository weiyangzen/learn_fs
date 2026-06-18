<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/implicit_dirs_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/implicit_dirs_test.go

## Purpose

This integration-style test suite validates a read-focused filesystem mount with implicit directories enabled. It checks how files, explicit directory placeholder objects, implicit directories from descendants, conflicts, unknown names, directory removal, timestamps, and symlink rename behavior appear through the mounted filesystem.

## Important APIs, Types, and Functions

`ImplicitDirsTest` embeds `fsTest` and enables `serverCfg.ImplicitDirectories`. Tests use `t.createObjects`, `storageutil`, direct bucket deletes, `fusetesting.ReadDirPicky`, `os.Stat`, `os.Lstat`, `os.Remove`, `os.Rename`, and symlink helpers.

Named cases include `NothingPresent`, `FileObjectPresent`, `DirectoryObjectPresent`, `ImplicitDirectory_DefinedByFile`, `ImplicitDirectory_DefinedByDirectory`, multiple `ConflictingNames_*` tests, `StatUnknownName_*`, `ImplicitBecomesExplicit`, `ExplicitBecomesImplicit`, `Rmdir_*`, `AtimeCtimeAndMtime`, and `RenameSymlinkToImplicitDir`.

## Control Flow

Each test seeds fake GCS object names out of band, performs POSIX operations through the mount, and asserts returned file info. Conflict tests create both `foo` and `foo/` or `foo/bar`, then verify listings prefer the directory as `foo` and expose the file or symlink as `foo\n`. Removal tests attempt to delete non-empty implicit directories, delete empty explicit placeholders, and verify directory contents after removal.

## State and Persistence Behavior

The fake bucket is the source of truth, while the mounted filesystem synthesizes implicit directories. Explicit placeholders can be added or removed during a test and subsequent stats should still classify the path correctly. File timestamps for implicit directories are derived from mount or clock state and only checked as "reasonable".

## Dependencies and Integration Points

The suite exercises the whole path from `dirInode` lookup/listing through `DirHandle` conflict resolution to FUSE-visible POSIX calls. It depends on storage object naming conventions, metadata symlink representation, FUSE testing helpers, and fake bucket operations.

## Risks and Edge Cases

Conflict suffix semantics are user-visible and rely on newline being illegal in GCS object names. Unknown-name checks protect prefix false positives such as `foo` vs `foop`. Rmdir behavior must distinguish empty explicit directories from implicit non-empty directories. Remote mutation between implicit and explicit forms must not break stat behavior.

## Test Signals

Signals include directory/file mode bits, sizes, nlink, symlink mode, readlink target, not-found detection, not-empty errors, empty parent listings after rmdir, and timestamp proximity.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/implicit_dirs_test.go -->
