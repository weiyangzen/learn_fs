## sources/user-network-fs/go-fuse/fuse/pathfs/locking.go

Purpose: serializing wrapper for pathfs `FileSystem` implementations that are not internally thread-safe.

Important APIs/types/functions: `lockingFileSystem`, `NewLockingFileSystem`, `locked`, and delegated methods for attrs, namespace operations, xattrs, mount hooks, open/create, directory reads, symlink/readlink, and statfs.

Control flow: most methods acquire a mutex via `locked()` defer-unlock pattern, call the wrapped filesystem, and return its result. `Create` locks while creating and wraps the returned file with `nodefs.NewLockingFile`; `Open` wraps the returned file with the same mutex without taking the filesystem lock around the open call in this file.

State and persistence: wrapper stores a mutex and inner filesystem; persistent data belongs to the inner filesystem.

Dependencies and integration: useful because FUSE dispatches operations concurrently.

Risks and test signals: coarse locking can reduce concurrency and deadlock if inner callbacks call back into the wrapper. The unlocked `Open` path is a notable behavior to preserve or review carefully if tightening synchronization.
