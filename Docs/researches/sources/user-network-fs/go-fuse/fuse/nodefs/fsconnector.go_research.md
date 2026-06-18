## sources/user-network-fs/go-fuse/fuse/nodefs/fsconnector.go

Purpose: core nodefs connector state machine translating kernel inode handles to Go `Inode` objects.

Important APIs/types/functions: `FileSystemConnector`, `NewOptions`, `NewFileSystemConnector`, `Server`, `SetDebug`, `verify`, `childLookup`, `toInode`, `lookupUpdate`, `forgetUpdate`, `InodeHandleCount`, `Node`, `LookupNode`, `mountRoot`, `Mount`, and `Unmount`.

Control flow: constructor creates root inode, mounts it, registers root lookup count, and later raw operations use `toInode`/lookup/forget paths. Lookup increments handle counts; forget decrements, potentially deleting nodes when deletable. Submount helpers attach additional roots.

State and persistence: maintains `inodeMap`, root node, server pointer, debug flag, and `lookupLock`. This is long-lived mount state, not durable beyond process.

Dependencies and integration: backs `nodefs.RawFS`, mount helpers, notification support, and pathfs.

Risks and test signals: lookup/forget races, stale handles, and submount lifecycle are high risk. Handle tests and fileless tests cover parts of this logic.
