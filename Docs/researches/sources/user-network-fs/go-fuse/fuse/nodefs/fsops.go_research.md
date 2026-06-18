## sources/user-network-fs/go-fuse/fuse/nodefs/fsops.go

Purpose: raw FUSE operation implementation for nodefs by adapting protocol structs to `Node` and `File` callbacks.

Important APIs/types/functions: `FileSystemConnector.RawFS`, `rawBridge`, and methods for `Lookup`, `Forget`, `GetAttr`, `OpenDir`, `ReadDir`, `ReadDirPlus`, `Open`, `SetAttr`, namespace ops, xattrs, `Create`, `Release`, `Read`, `Write`, locks, `StatFs`, `Flush`, `CopyFileRange`, `Lseek`, `Statx`, `OnUnmount`, and `Ioctl`.

Control flow: each raw request resolves an inode/file handle, builds a `fuse.Context`, invokes node or file methods, fills protocol outputs, and updates handle/lookup tables. Create/open register files; release/forget unregister.

State and persistence: mutates connector inode map, inode file lists, lookup counts, and file handle maps. Backing persistence is delegated to nodes/files.

Dependencies and integration: core bridge between `fuse.Server` and deprecated nodefs API.

Risks and test signals: nil file handles, concurrent close/stat, lookup/forget ordering, and xattr sizing are high risk. `fileless_test.go`, `handle_test.go`, and broader FUSE tests cover these paths.
