## sources/user-network-fs/go-fuse/fuse/api.go

Purpose: public raw FUSE API documentation and core interfaces for implementing a filesystem at protocol level.

Important APIs/types/functions: `ReadResult` abstracts read data as bytes, fd-backed ranges, or pipe-backed data. `MountOptions` controls kernel mount negotiation, caching, capabilities, logging, direct mount, idmapped mount, passthrough, xattrs, locks, splice, panic handling, and request limits. `RawFileSystem` declares callbacks for lookup, attrs, namespace mutation, xattrs, file I/O, locks, directory I/O, statfs, statx, init, and unmount.

Control flow: `fuse.NewServer` mounts and dispatches kernel requests to `RawFileSystem` methods, typically concurrently. `Serve` may run in foreground or goroutine; callers wait with `WaitMount`.

State and persistence: the file defines contracts only. Implementations must own thread-safe inode/file state and must not retain reused request buffers without copying.

Dependencies and integration: foundation for the higher-level `fs`, deprecated `nodefs`, and `pathfs` packages.

Risks and test signals: incorrect implementations can deadlock, race on request memory, or mishandle interrupts. Many tests in this subset validate options and raw dispatch behavior.
