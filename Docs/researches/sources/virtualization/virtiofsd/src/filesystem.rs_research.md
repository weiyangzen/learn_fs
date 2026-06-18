# File Research: sources/virtualization/virtiofsd/src/filesystem.rs

## Scope

Transport-facing filesystem trait and shared request/response types. This file defines the contract between the FUSE/vhost-user server and concrete filesystem implementations such as passthrough.

## APIs Covered

- `Entry`, `DirEntry`, `GetxattrReply`, `ListxattrReply`.
- `ZeroCopyReader` and `ZeroCopyWriter`.
- Request context: `Context`, `Extensions`, `SecContext`.
- `DirectoryIterator`.
- Main `FileSystem` trait with FUSE operations.
- `SerializableFileSystem` migration trait.

## Behavior

- `Entry` converts to `fuse::EntryOut`, preserving inode, generation, attributes, and cache timeouts.
- `Context` maps FUSE header UID/GID/PID into guest-aware IDs.
- `FileSystem` defines lookup-count semantics and default behavior for most FUSE operations.
- Most unimplemented operations return `ENOSYS`, matching FUSE permanent-disable or success semantics where documented.
- `open()` and `opendir()` default to no handle and empty open options.
- `statfs()` defaults to libfuse-like minimal values.
- Read/write use zero-copy reader/writer traits rather than fixed intermediate buffers.
- `SerializableFileSystem` splits migration into optional preparation, serialization, and destination-side application.

## Invariants

Implementers must maintain inode lookup counts, handle valid kernel caching timeouts, honor open flags, xattr size semantics, directory offsets, writeback-cache caveats, and migration cancellation expectations.
