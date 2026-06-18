# `sources/user-network-fs/go-fuse/fuse/pathfs/pathfs.go`

## Purpose
Bridges the path-oriented `pathfs.FileSystem` API to `nodefs.Node`/inode operations. It keeps enough inode tree state to translate kernel inode callbacks back into paths and to optionally coalesce hard links by client inode number.

## Important APIs, Types, And Functions
Defines `PathNodeFs`, `pathInode`, `refCountedInode`, `NewPathNodeFs`, `Mount`, `Unmount`, `Node`, `LookupNode`, `Path`, `Notify`, `FileNotify`, `EntryNotify`, `AllFiles`, and the full node operation surface (`Lookup`, `Open`, `Create`, `GetAttr`, `Chmod`, `Utimens`, locking, xattrs).

## Control Flow
Mounting stores the connector and invokes the wrapped filesystem. Most operations call `GetPath()` then delegate to the wrapped `FileSystem`; successful create/mkdir/symlink/link/lookup operations add child inodes. `Lookup` removes stale known children when type or existence changed, then either finds an existing client inode or creates a new child.

## State And Persistence
State is in the node tree plus `clientInodeMap`, guarded by `pathLock`. `clientInode` reference counts model hard-link aliases and are cleared by forget/removal paths. Deleted open files get synthetic `.deleted.<inode>` paths so file-handle fallbacks can still work where possible.

## Dependencies And Integration Points
Integrates tightly with `fuse/nodefs`, `fuse` request types, and the wrapped `pathfs.FileSystem`. It is the adapter used by loopback, prefix, readonly, locking, and many tests.

## Risks And Edge Cases
Correctness depends on lock discipline around client inode references and on fallback ordering from file-handle methods to path methods. Rename/remove races can leave temporary stale children, and hard-link support is disabled unless `ClientInodes` is set.

## Test Signals
Covered by loopback hard-link tests, lookup-known-children cache tests, mount/unmount tests, fsetattr tests, cache invalidation tests, and race-oriented getattr tests.
