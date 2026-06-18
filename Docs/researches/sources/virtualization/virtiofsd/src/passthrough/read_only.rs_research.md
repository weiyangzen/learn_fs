# File Research: sources/virtualization/virtiofsd/src/passthrough/read_only.rs

This file implements a read-only wrapper around `PassthroughFs` while preserving the same `FileSystem` and `SerializableFileSystem` interfaces.

Core type:
- `PassthroughFsRo(PassthroughFs)`: owns an inner passthrough filesystem and restricts mutating operations.

Open filtering:
- `rofs_open()` allows `O_PATH` opens directly because `O_PATH` ignores most access flags.
- Non-`O_RDONLY` access modes return `EROFS`.
- `O_EXCL` returns `EROFS`.
- `O_TMPFILE` and `O_TRUNC` return `EINVAL`.
- `O_CREAT` is stripped and the underlying open is attempted; if the path does not exist, the wrapper returns `EROFS`.

Delegation helpers:
- `ops_allow!` generates methods that forward directly to the inner filesystem.
- `ops_forbid!` generates methods that always return `EROFS`.

Allowed operations:
- Init/destroy, lookup/forget, getattr, readlink/read, flush, fsync, release, statfs, get/list xattr, readdir, fsyncdir, releasedir, lseek, and syncfs are allowed.

Forbidden operations:
- setattr, symlink, mknod, mkdir, unlink, rmdir, rename, link, write, fallocate, setxattr, removexattr, and copyfilerange return `EROFS`.

Special operations:
- `open()` and `opendir()` apply `rofs_open()` before delegating.
- `create()` never creates; it performs lookup and open on an existing file, returning `EROFS` if lookup reports not found.
- `access()` rejects `W_OK` with `EROFS` and delegates all other checks.
- Serialization methods delegate directly, so read-only instances still support migration.

Edge cases and risks:
- The wrapper intentionally returns `EROFS` earlier than Linux might in some cases, for example when a writable filesystem would have returned `EEXIST`.
- Read-only mode still allows fsync/syncfs and metadata reads.
- Xattr reads are allowed, but all xattr writes/removals are blocked.
