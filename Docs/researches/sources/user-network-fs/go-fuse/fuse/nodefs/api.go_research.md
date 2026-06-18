## sources/user-network-fs/go-fuse/fuse/nodefs/api.go

Purpose: deprecated inode-oriented high-level API predating `fs`.

Important APIs/types/functions: `Node` interface defines inode tree, namespace, attributes, xattrs, file I/O, locks, and statfs callbacks. `File` interface defines open-file operations and lifecycle. `WithFlags` carries open file plus FUSE/open flags. `Options` configures timeouts, owner rewriting, debug, and lookup behavior.

Control flow: `FileSystemConnector` translates raw FUSE requests to `Node` and `File` methods; users embed default implementations and override methods.

State and persistence: implementations own their node and file state; connector manages inode/file handles and lookup counts.

Dependencies and integration: bridges to `fuse.RawFileSystem` and underlies deprecated `pathfs`.

Risks and test signals: API is broad and concurrency-sensitive. Incorrect Node/File implementations can leak handles or mis-handle kernel forgets.
