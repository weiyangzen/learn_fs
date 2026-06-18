# File Research: sources/virtualization/virtiofsd/src/passthrough/mod.rs

This is the main passthrough filesystem implementation. It defines configuration, runtime state, helper logic, and the `FileSystem` implementation that forwards FUSE operations to the host filesystem.

Major public modules:
- Re-exports and submodules include credentials, device migration state, file handles, inode store, mount FD management, read-only wrapper, stat helpers, utility helpers, and xattr mapping.

Configuration:
- `CachePolicy`: `Never`, `Metadata`, `Auto`, `Always`.
- `InodeFileHandlesMode`: `Never`, `Prefer`, `Mandatory`.
- `MigrationOnError`: `Abort` or `GuestError`.
- `MigrationMode`: `FindPaths` or `FileHandles`.
- `Config`: timeouts, cache/writeback, root directory, proc fds, submounts, file-handle mode, xattr and security-label behavior, ACLs, migration behavior, ID maps, and guest FD limit.

Runtime state:
- `PassthroughFs` holds `InodeStore`, open handle map, guest FD semaphore, optional `MountFds`, `/proc/self/fd`, original cwd, negotiated option flags, OS facts, migration tracking flag, config, and UID/GID maps.
- `HandleData` tracks open handle ownership, wrapped file or invalid migration error, and handle migration info.
- `ScopedWorkingDirectory` temporarily switches cwd to `/proc/self/fd` for path-based syscalls against O_PATH descriptors.

Initialization:
- `PassthroughFs::new()` opens proc fds or consumes sandbox-provided ones, initializes `MountFds` when needed, builds soft ID maps, detects remapped `security.capability`, validates file-handle support, and clears umask.
- `init()` resets prior state, opens root, negotiates FUSE options, records negotiated state, and validates required capabilities for ACLs and security labels.
- `open_root_node()` creates the root `InodeData`, gives it root migration info when possible, and assigns libfuse-like refcount 2.

Lookup and open behavior:
- `open_relative_to()` uses `openat2` when available and falls back to `openat`.
- `try_lookup_implementation()` opens a child as `O_PATH`, stats it, optionally creates a file handle, and claims an existing inode by handle or IDs.
- `do_lookup()` creates new inode entries, marks submounts, attaches migration info if migration tracking is active, and leaks one strong reference to the guest.
- `open_inode()` handles writeback read/write upgrade, writeback append clearing, optional `O_DIRECT` filtering, and then reopens by proc path or file handle.
- `do_open()` cleans flags, optionally drops `FSETID`, opens the inode, clears capabilities on truncate, stores a handle, and chooses FUSE open cache options.

Mutation and migration consistency:
- `before_invalidating_path()` looks up an inode before unlink/overwrite-style operations.
- `after_invalidating_path()` clears path-based migration info after the syscall and tries to rediscover the inode through `/proc/self/fd`.
- `update_inode_migration_info()` refreshes path migration info after successful rename.
- These hooks appear around `unlink`, `rmdir`, `mkdir`, `rename`, `mknod`, `link`, and `symlink`.

Filesystem operations:
- Implements statfs, lookup, forget, batch_forget, opendir/releasedir, readdir, open/release, create, unlink/rmdir, read/write, getattr/setattr, rename, mknod, link, symlink, readlink, flush, fsync/fsyncdir, access, xattr operations, fallocate, lseek, copyfilerange, and syncfs.
- Readdir serializes kernel directory offset access with a write lock around `lseek64`/`getdents64`.
- Reads and writes use zero-copy helpers and offset-based syscalls so file offsets are not shared.
- Write paths clear remapped file capabilities and handle append semantics with `RWF_APPEND` only for non-delayed writes.

Xattr and privilege behavior:
- Blocks POSIX ACL xattrs unless ACL support is negotiated.
- Applies `XattrMap` on client names and server xattr lists.
- Clears remapped `security.capability` on writes, truncates, chown, and relevant xattr paths.
- Clears SGID explicitly for POSIX ACL setxattr when requested by `SETXATTR_ACL_KILL_SGID`.
- `unix_credentials_guard()` maps guest credentials to host credentials and handles supplementary groups when negotiated.

Tests:
- Two unit tests cover SGID clearing decision for non-UTF-8 xattr names and `system.posix_acl_access`.

Edge cases and risks:
- This file is syscall-heavy and depends on correct `O_PATH`, `/proc/self/fd`, and `openat2`/`openat` behavior.
- File-handle mode has early validation and per-filesystem error suppression, but support can vary by underlying filesystem.
- Writeback caching intentionally trades consistency for performance when users assert exclusive directory access.
- Migration consistency relies on best-effort rediscovery after path invalidation and on preserialization/confirmation phases.
