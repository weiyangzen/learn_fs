# sources/sync-backup/kopia/internal/mockfs/mockfs.go

Purpose: implements an in-memory `fs` tree for tests, including directories, files, symlinks, device metadata, and entries that intentionally return errors.

Important APIs/types/functions: `Directory`, `File`, `Symlink`, `ErrorEntry`, `ReaderSeekerCloser`, `NewDirectory`, `NewFile`, `AddFile*`, `AddDir*`, `AddSymlink`, `Subdir`, `Remove`, `FailReaddir`, `OnReaddir`, `Child`, `Iterate`, `Open`, and `Resolve`.

Control flow: add methods resolve slash-separated child paths, create typed entries with `DefaultModTime`, append and sort children, and expose `fs.Directory` iteration through `fs.StaticIterator`. File open invokes a source factory to support dynamic content or injected read failures. Symlink resolution starts from parent or root for absolute targets and follows mock Unix-style separators.

State and persistence behavior: all state is in memory: parent pointers, sorted child slices, file source closures, readdir callbacks, and stored device/owner metadata. There is no locking, so callers should treat it as test-local.

Dependencies and integration points: satisfies Kopia `fs.Directory`, `fs.File`, `fs.Symlink`, and `fs.ErrorEntry` interfaces and is used by snapshot, upload, restore, mount, and policy tests.

Risks and test signals: `resolveSubdir("..")` assumes a parent exists, duplicate names are not rejected, file `SetContents` does not update size, and symlink target indexing assumes non-empty target. Useful tests cover ordering, nested path resolution, injected errors, absolute/relative symlinks, and metadata propagation.
