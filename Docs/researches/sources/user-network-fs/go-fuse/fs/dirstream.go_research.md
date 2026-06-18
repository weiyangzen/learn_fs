# sources/user-network-fs/go-fuse/fs/dirstream.go

Purpose: implements in-memory and loopback directory-stream adapters used by bridge directory operations.

Important types/functions: `dirArray` wraps `[]fuse.DirEntry` with sequential offsets and seek support; `NewListDirStream`; `dirStreamAsFile` adapts a `DirStream` creator to file-handle readdir/release/seek interfaces; `loopbackDirStream` reads OS directory entries via `getdents`, buffers raw records, parses them with `fuse.DirEntry.Parse`, supports `Seekdir`, `Fsyncdir`, `Releasedir`, and ioctl forwarding.

Control flow/state: `loopbackDirStream` owns an fd, buffer, pending bytes, and pending errno under mutex. `load` lazily refills only when no pending entries/error exist.

Dependencies/integration: used by `LoopbackNode.OpendirHandle`, bridge fallback directory listing, and tests. Risks include fd lifecycle, platform `getdents` differences, unsafe ioctl buffer indexing when input/output slices are empty, and directory offset correctness. Tests cover seek, errors, fsyncdir, caching, and loopback dirs.
