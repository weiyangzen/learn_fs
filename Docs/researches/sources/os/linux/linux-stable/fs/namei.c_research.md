# File Research: sources/os/linux/linux-stable/fs/namei.c

## Purpose

Implements Linux VFS pathname resolution, filename import, permission checks, dcache lookup, symlink following, mount traversal, open/create handling, namespace mutation operations, and generic symlink page-cache helpers.

## Main Entry Points

- Filename handling: `filename_init()`, `getname_flags()`, `getname_uflags()`, `getname_kernel()`, `putname()`, delayed filename helpers.
- Permissions: `generic_permission()`, `inode_permission()`, `may_linkat()`, `may_create_dentry()`, `may_delete_dentry()`.
- Path lookup: `filename_lookup()`, `kern_path()`, `vfs_path_lookup()`, `vfs_path_parent_lookup()`, `user_path_at()`.
- Single-component lookup helpers: `lookup_one*()`, `lookup_noperm*()`, `try_lookup_noperm()`.
- Open path: `do_file_open()`, `do_file_open_root()`, `path_openat()`, `vfs_tmpfile()`, `kernel_tmpfile_open()`, `dentry_create()`.
- Creation and mutation: `vfs_create()`, `vfs_mknod()`, `vfs_mkdir()`, `vfs_rmdir()`, `vfs_unlink()`, `vfs_symlink()`, `vfs_link()`, `vfs_rename()`.
- Syscall implementations: `mknod`, `mkdir`, `rmdir`, `unlink`, `symlink`, `link`, `rename`.
- Symlink helpers: `vfs_readlink()`, `vfs_get_link()`, `page_get_link()`, `page_readlink()`, `page_symlink()`.

## Control Flow And State

Path walking is centered on `struct nameidata`. `path_init()` chooses the starting path from root, cwd, dirfd, or a supplied root and can enter RCU-walk. `link_path_walk()` iterates components, checks directory search permission, hashes each component, handles `.`, `..`, trailing slashes, nested symlinks, and transitions through `walk_component()`. Lookup first tries lockless dcache lookup and revalidation; slow lookup allocates or waits on in-lookup dentries under the parent inode lock.

RCU-walk falls back to ref-walk through `try_to_unlazy()` or `try_to_unlazy_next()` when blocking work, unstable seqcounts, managed dentries, or filesystem revalidation require references. Mount traversal handles mountpoint crossing, automounts, `LOOKUP_NO_XDEV`, `LOOKUP_BENEATH`, `LOOKUP_IN_ROOT`, scoped lookup escape checks, and `..` across mount roots. Symlink following uses a bounded stack, enforces `MAXSYMLINKS`, handles absolute symlink targets by jumping to root, and supports magic-link jumps through `nd_jump_link()`.

Open handling uses `open_last_lookups()` and `lookup_open()` to resolve the final component, optionally create it, and use filesystem `atomic_open()` when available. `do_open()` completes the walk, enforces `O_EXCL`, `O_DIRECTORY`, sticky-directory protections, `may_open()`, LSM post-open hooks, and `O_TRUNC`.

Filesystem mutation paths first resolve the parent, obtain mount write access, lock parent directories through `start_dirop()` or rename-specific locking, run VFS permission and idmapping checks, call LSM hooks, break delegations when required, invoke the filesystem inode operation, and emit fsnotify events. Rename uses `s_vfs_rename_mutex` and ordered child locking to avoid directory loops and deadlocks, then calls filesystem `->rename()` and updates dcache with `d_move()` or `d_exchange()` unless the filesystem handles it itself.

## Dependencies

Depends on dcache, mount namespace internals from `mount.h`, `mount_lock` and `rename_lock` seqcounts, RCU, POSIX ACLs, LSM hooks, audit, fsnotify, idmapped mounts, device cgroups, file leases/delegations, open flags, user-copy helpers, folio/page-cache helpers, and per-filesystem inode/dentry operation tables.

## Risks

This is one of the most concurrency-sensitive VFS files. Correct behavior depends on matching RCU seqcount validation with reference acquisition, preventing scoped lookup escapes during rename or mount races, preserving mount and dentry lifetimes, enforcing trailing slash and symlink semantics, and maintaining strict rename locking order. Security-sensitive behavior includes sticky directory checks, protected symlink/hardlink/fifo/regular sysctls, idmapped ownership checks, device-node restrictions, noexec/nodev handling, and LSM hook ordering. Delegation retry paths must drop locks before waiting and then repeat lookup safely.
