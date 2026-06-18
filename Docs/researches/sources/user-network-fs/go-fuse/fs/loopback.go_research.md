# sources/user-network-fs/go-fuse/fs/loopback.go

Purpose: implements the main loopback filesystem node that delegates FUSE operations to an underlying POSIX filesystem.

Important APIs/types/functions: `LoopbackRoot` holds backing path, device, optional `NewNode`, and root node; `LoopbackNode` embeds `Inode` and implements statfs, lookup, mknod, mkdir, rmdir, unlink, rename, create, symlink, link, readlink, open, opendir/readdir, getattr, setattr, xattrs, copy_file_range, and root construction. `idFromStat` combines device/inode into stable attrs. `path`/`relativePath` map inodes to backing paths.

Control flow/state: persistent state is the backing filesystem. New children are created from backing `stat` data. Root-owned paths and cross-root renames are guarded. Root preserves caller owner when running as root.

Dependencies/integration: uses syscalls, `openat.OpenSymlinkAware`, `renameat`, unix xattrs, and `LoopbackFile`. Risks include TOCTOU around paths, symlink safety, inode reuse, path lookup for orphaned nodes, ownership/chown failures ignored in create paths, and platform-specific copy/statx behavior. Tests cover rename exchange, non-root loopback subtree, xattrs, copy, mknod, ioctl, and direct mount.
