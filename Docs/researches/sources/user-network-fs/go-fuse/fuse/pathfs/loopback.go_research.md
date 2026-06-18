# `sources/user-network-fs/go-fuse/fuse/pathfs/loopback.go`

## Purpose
Implements `NewLoopbackFileSystem`, a pathfs `FileSystem` backed by a real directory. It translates virtual paths with `GetPath` and delegates stat, open, directory listing, metadata mutation, links, and create/delete operations to the host OS.

## Important APIs, Types, And Functions
`loopbackFileSystem`, `NewLoopbackFileSystem`, `StatFs`, `GetAttr`, `OpenDir`, `Open`, `Create`, `Access`, and path-based chmod/chown/truncate/link/rename methods. `Open` and `Create` return `nodefs.NewLoopbackFile` handles.

## Control Flow
Construction canonicalizes the root to an absolute path. Reads and metadata requests join the FUSE-relative name to `Root`; root getattr follows symlinks with `Stat`, while non-root entries use `Lstat`. Directory reads batch `Readdir(500)` into `fuse.DirEntry` values.

## State And Persistence
Persistent state is only the absolute backing `Root`; all file data and metadata persist in the underlying filesystem. `Access` computes permissions from fetched attributes and caller credentials rather than relying on kernel `access`.

## Dependencies And Integration Points
Depends on `os`, `syscall`, `filepath`, `nodefs`, `fuse`, and `internal.HasAccess`. It is commonly wrapped by `PathNodeFs` and `NewLockingFileSystem` in tests.

## Risks And Edge Cases
Path joining intentionally exposes the backing tree semantics; symlink behavior is host-filesystem behavior. `Open` strips `O_APPEND` because kernel offsets are expected to handle append, and `Create` returns a loopback file even when `os.OpenFile` returns an error, so callers must trust the status.

## Test Signals
Exercised by loopback integration tests covering read/write-through, hard links, POSIX operations, statfs parity, symlink roots, access checks, large IO, and utimens behavior.
