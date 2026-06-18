## sources/user-network-fs/go-fuse/fuse/nodefs/defaultnode.go

Purpose: null `Node` implementation for embedding in nodefs nodes.

Important APIs/types/functions: `NewDefaultNode` returns a node that stores its inode pointer and implements mount hooks, lookup, namespace operations, xattrs, attrs, locks, read/write, and metadata operations with default errors or no-ops.

Control flow: callbacks return `ENOSYS`, `ENOENT`, or reasonable defaults. `OpenDir` can synthesize entries from known children when no custom directory reader exists.

State and persistence: stores only the associated `*Inode`; user embedding types provide actual state.

Dependencies and integration: baseline for `memNode`, tests, and user nodefs implementations.

Risks and test signals: defaults must be compatible with kernel expectations; wrong default errors can change user-visible read-only behavior or directory listing semantics.
