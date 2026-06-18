## sources/user-network-fs/go-fuse/fuse/nodefs/fileless_test.go

Purpose: tests nodefs support for files that return no file handle and serve reads directly from the node.

Important APIs/types/functions: `nodeReadNode` implements `Open`, `Read`, `GetAttr`, and `Lookup`. `newNodeReadNode` configures no-open and directory modes. `TestNoOpen` and `TestNodeRead` mount variants and read through the kernel.

Control flow: lookup creates child nodes, open may return nil, and read is dispatched to node-level `Read` when no `File` handle exists.

State and persistence: data is held in `nodeReadNode` byte slices. No durable backing store.

Dependencies and integration: targets rawBridge dispatch in `nodefs/fsops.go` for nil file handle paths.

Risks and test signals: protects no-open support and direct node read fallback. Regressions can cause `EBADF`, `ENOSYS`, or nil dereference.
