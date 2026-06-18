## sources/user-network-fs/go-fuse/fuse/pathfs/api.go

Purpose: deprecated path-based filesystem API layered on nodefs.

Important APIs/types/functions: `FileSystem` interface defines path-string callbacks for attrs, namespace mutation, xattrs, mount hooks, open/create, directory reads, symlinks, and statfs. `PathNodeFsOptions` configures client inode usage and debug.

Control flow: `PathNodeFs` translates inode requests into path strings and calls this interface; implementations usually embed `NewDefaultFileSystem`.

State and persistence: API itself owns no state; implementers store backing path or virtual tree state.

Dependencies and integration: depends on `fuse.Context` and `nodefs.File`, and is marked deprecated in favor of `fs`.

Risks and test signals: path-based APIs are simpler but can struggle with hardlinks, renames, and concurrent mutation. Loopback/pathfs tests cover common behavior.
