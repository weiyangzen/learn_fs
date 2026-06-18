<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/serve.go -->
# sources/user-network-fs/bazil-fuse/fs/serve.go

Purpose: core high-level FUSE service loop that maps kernel FUSE requests onto Go `FS`, `Node`, and `Handle` interfaces and exposes cache/notification helpers.

Important APIs, types, and functions: defines `FS`, `Node`, many optional `Node*` interfaces, `Handle` and optional `Handle*` interfaces, `Config`, `Server`, `New`, `Serve`, `DataHandle`, and `GenerateDynamicInode`. Internal state types include `serveNode`, `serveHandle`, and `serveRequest`.

Control flow: `Server.Serve` obtains the root node, registers it as NodeID 1, reads requests from `fuse.Conn`, and handles each in a goroutine. `serve` sets up context cancellation, request tracking, panic/Goexit protection, debug logging, and delegates to `handleRequest`. `handleRequest` switches over concrete request types for statfs, attrs, lookup, create, open, read/write, flush/release, forget, xattrs, locks, poll, fallocate, interrupts, destroy, and notify replies.

State and persistence behavior: server state is in-memory maps/slices for node IDs, handles, reference counts, pending requests, free lists, and notify wait channels, protected by mutexes. Filesystem persistence is delegated to user implementations. Kernel cache state is manipulated through invalidation and notify methods.

Dependencies and integration points: integrates the low-level `bazil.org/fuse` protocol package, `fuseutil.HandleRead`, `golang.org/x/sys/unix` lock constants, user filesystem implementations, and kernel notification APIs.

Risks and test signals: key risks are NodeID/refcount mismatches, stale handle access, duplicate request IDs, handler panics, context cancellation semantics, notify sequence exhaustion, and dynamic inode collisions. Tests should exercise every optional interface path, forget/batch-forget, interrupts, locks, cache invalidation, notify retrieve/store/delete, and panic/error conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/serve.go -->
