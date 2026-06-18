# sources/user-network-fs/go-fuse/fs/api.go

Purpose: public contract for the tree-based go-fuse filesystem API. The top-level documentation explains inode-based design, kernel caches, interrupts, locking/deadlock caveats, dynamic lookup/readdir, and static persistent in-memory trees.

Important APIs/types: `InodeEmbedder`; many optional `Node*` operation interfaces for statfs, access, getattr/setattr, xattrs, link/symlink/create/rename, read/write/fsync/flush/release, fallocate, copy_file_range, statx, lseek, locks, ioctl, lifecycle; `DirStream`; file-handle interfaces such as `FileReader`, `FileWriter`, `FileReaddirenter`, `FileSeekdirer`, and `FilePassthroughFder`; `Options` for cache TTLs, automatic inode numbering, root `OnAdd`, permissions, UID/GID defaults, test callbacks, logging, and root stable attrs.

Control flow/state: interfaces are implemented by user nodes and dispatched by `bridge.go`. `Options` influences default attr rewriting, cache timeouts, negative lookup caching, and mount behavior.

Risks/test signals: API stability is critical. Risks include subtle defaults (`Unlink`/`Rmdir` default success, zero permissions rewritten unless `NullPermissions`), interrupt handling expectations, and deterministic `Readdir` requirements. Broad tests in this subset exercise direct I/O, caching, rename, forget, statx, ioctl, and loopback integration.
