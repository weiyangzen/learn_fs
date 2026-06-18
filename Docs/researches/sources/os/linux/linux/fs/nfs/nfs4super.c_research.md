# File Research: sources/os/linux/linux/fs/nfs/nfs4super.c

## Purpose

`nfs4super.c` wires NFSv4 into the Linux VFS superblock and module framework. It defines NFSv4 superblock operations, the NFSv4 subversion descriptor, mount/referral tree construction, inode writeback/eviction behavior, and module initialization/exit for NFSv4-only services.

## Superblock Integration

- `nfs4_sops` installs common NFS inode allocation/freeing, statfs, mount display, stats, drop inode, and unmount behavior, while overriding writeback and eviction with NFSv4-aware functions.
- `nfs_v4` advertises the NFSv4 subversion with:
  - `owner = THIS_MODULE`
  - filesystem type `nfs4_fs_type`
  - RPC version table `nfs_version4`
  - client operations `nfs_v4_clientops`
  - super operations `nfs4_sops`
  - NFSv4 xattr handlers

## Inode Writeback and Eviction

- `nfs4_write_inode()` first calls generic `nfs_write_inode()`, then commits pNFS layout metadata with `pnfs_layoutcommit_inode()` when normal inode writeback succeeds. Synchronous writeback maps to synchronous layout commit.
- `nfs4_evict_inode()` performs final page truncation and inode clearing, returns and frees any delegation, returns pNFS layout state, destroys final layout structures, runs generic NFS inode cleanup, and zaps the NFSv4 xattr cache.
- The eviction order matters: delegation return can trigger pNFS return-on-close, then explicit layout return and final layout destruction clean remaining layout state before generic NFS inode cleanup.

## Referral Loop Protection

The file implements a per-task referral recursion guard:

- `struct nfs_referral_count` records the current task and referral nesting depth.
- `nfs_referral_count_list` plus `nfs_referral_count_list_lock` maintain active per-task entries.
- `NFS_MAX_NESTED_REFERRALS` limits nested referral traversal to 2.
- `nfs_referral_loop_protect()` allocates or increments the current task entry and returns `-ELOOP` when the nesting limit is exceeded.
- `nfs_referral_loop_unprotect()` decrements and frees the task entry when the nesting count reaches zero.

## NFSv4 Mount Construction

`do_nfs4_mount()` implements the common mount path for normal NFSv4 mounts and referral mounts:

- It accepts a pre-created `nfs_server` or an error pointer.
- It duplicates the caller's `fs_context` using `vfs_dup_fs_context()`.
- It marks the duplicated context internal and installs the server object in the root context.
- It propagates `fscache_uniq` when present.
- It synthesizes a root source string as `host:/` or `[ipv6-host]:/`.
- It mounts the server root with `fc_mount()`.
- It applies referral loop protection while `mount_subtree()` walks from the server root to the requested export path.
- It stores the resulting dentry in the original fs context as `fc->root`.

The caller deliberately leaves the duplicated root context export path unset because server-root discovery does not use the original export path.

## Public Mount Entry Points

- `nfs4_try_get_tree()` creates a normal NFSv4 server with `nfs4_create_server()` and mounts the requested remote export path by walking from the server root.
- `nfs4_get_referral_tree()` creates a referral server with `nfs4_create_referral_server()` and uses the same root-walk mechanism for referral traversal.
- Both functions log mount diagnostics, report a user-facing mount error message when remote path following fails, and return the `do_nfs4_mount()` status.

## Module Initialization and Exit

`init_nfs_v4()` initializes NFSv4 support in dependency order:

1. DNS resolver support via `nfs_dns_resolver_init()`
2. NFSv4 idmapper via `nfs_idmap_init()`
3. NFSv4.2 xattr cache when `CONFIG_NFS_V4_2` is enabled
4. NFSv4 sysctl registration
5. NFSv4.2 server-side-copy operations registration
6. NFSv4 subversion registration with `register_nfs_version(&nfs_v4)`

Failure unwinds initialized pieces in reverse order. `exit_nfs_v4()` unloads conditional pNFS v3 data-server connection support, unregisters NFSv4, tears down xattr and copy operations for NFSv4.2, unregisters sysctls, and destroys idmap and DNS resolver resources.

## Cross-File Relationships

- Calls pNFS helpers from `pnfs.h` for layout commit, layout return, and final layout destruction.
- Calls delegation eviction helper `nfs_inode_evict_delegation()`.
- Registers sysctls implemented in `nfs4sysctl.c`.
- Uses NFSv4 xattr cache helpers initialized for NFSv4.2.
- Registers the NFSv4 subversion consumed by generic NFS client mount code.

## Research Notes

This file is small but central to NFSv4 activation. The most notable behavior is the two-stage NFSv4 mount: mount the server pseudo-root internally, then use `mount_subtree()` to reach the requested export, with explicit loop protection for referral recursion.
