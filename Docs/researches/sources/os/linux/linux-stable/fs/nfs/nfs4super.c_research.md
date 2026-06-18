# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4super.c

## Purpose

`nfs4super.c` wires NFSv4 into the Linux VFS/module infrastructure. It defines NFSv4 superblock operations, the `nfs_subversion` registration record, NFSv4 inode writeback/eviction handling, referral-safe NFSv4 mounting, and module init/exit.

## NFSv4 Super Operations

`nfs4_sops` installs:
- `nfs_alloc_inode`
- `nfs_free_inode`
- `nfs4_write_inode`
- `nfs_drop_inode`
- `nfs_statfs`
- `nfs4_evict_inode`
- `nfs_umount_begin`
- `nfs_show_options`
- `nfs_show_devname`
- `nfs_show_path`
- `nfs_show_stats`

`nfs_v4` registers the NFSv4 subversion:
- file system type: `nfs4_fs_type`
- RPC version: `nfs_version4`
- client ops: `nfs_v4_clientops`
- super ops: `nfs4_sops`
- xattr handlers: `nfs4_xattr_handlers`

## Writeback

`nfs4_write_inode()` first delegates to generic NFS writeback via `nfs_write_inode()`. If that succeeds, it commits pNFS layout metadata with `pnfs_layoutcommit_inode()`, passing synchronous mode when writeback is `WB_SYNC_ALL`.

This means VFS inode writeback for NFSv4 includes both ordinary NFS dirty state and pNFS layout commit state.

## Inode Eviction

`nfs4_evict_inode()` performs NFSv4-specific cleanup in this order:
1. `truncate_inode_pages_final()`
2. `clear_inode()`
3. return/free any delegation with `nfs_inode_evict_delegation()`
4. return pNFS layout with `pnfs_return_layout()`
5. destroy final pNFS layout state with `pnfs_destroy_layout_final()`
6. run generic `nfs_clear_inode()`
7. zap NFSv4 xattr cache with `nfs4_xattr_cache_zap()`

The comment notes that delegation return can trigger pNFS return-on-close behavior, so pNFS cleanup follows delegation cleanup.

## Referral Loop Protection

The file maintains a global list of per-task `nfs_referral_count` records protected by `nfs_referral_count_list_lock`.

`nfs_referral_loop_protect()`:
- allocates a counter record,
- finds the current task in the list,
- increments referral depth if present,
- rejects depth `>= NFS_MAX_NESTED_REFERRALS`,
- inserts a new record if not present.

`NFS_MAX_NESTED_REFERRALS` is `2`.

`nfs_referral_loop_unprotect()` decrements the current task's referral count and frees the record when it reaches zero.

This prevents infinite or excessive nested referral traversal during NFSv4 mount path walking.

## Mount Flow

`do_nfs4_mount()` is the common mount implementation used for both normal and referral mounts.

Main flow:
1. Validate/create `nfs_server`.
2. Duplicate the original fs context with `vfs_dup_fs_context()`.
3. Clear duplicated source string.
4. Mark root context internal and attach the pre-created server.
5. Propagate `fscache_uniq` by parsing `fsc=` into the root context.
6. Build a root source string as either `host:/` or `[ipv6-host]:/`.
7. Mount the server root with `fc_mount()`.
8. Enter referral loop protection.
9. Use `mount_subtree()` to walk to the requested export path.
10. Store resulting dentry in `fc->root`.

Normal NFSv4 mounts call:
- `nfs4_try_get_tree()`: creates a server with `nfs4_create_server()` and calls `do_nfs4_mount()`.

Referral mounts call:
- `nfs4_get_referral_tree()`: creates a referral server with `nfs4_create_referral_server()` and calls `do_nfs4_mount()`.

Both functions log errors through `nfs_ferrorf()` and debug tracing.

## Module Initialization

`init_nfs_v4()` initializes in this order:
1. DNS resolver: `nfs_dns_resolver_init()`
2. idmapper: `nfs_idmap_init()`
3. NFSv4.2 xattr cache if enabled: `nfs4_xattr_cache_init()`
4. sysctl registration: `nfs4_register_sysctl()`
5. NFSv4.2 server-side copy ops if enabled: `nfs42_ssc_register_ops()`
6. subversion registration: `register_nfs_version(&nfs_v4)`

On failure it unwinds idmap and DNS resolver initialization. The single `out2` label is used both after xattr-cache failure and sysctl failure, so with `CONFIG_NFS_V4_2` a sysctl failure path calls `nfs_idmap_quit()` and DNS cleanup but does not call `nfs4_xattr_cache_exit()` in this file's visible code.

## Module Exit

`exit_nfs_v4()`:
1. unloads conditional pNFS v3 data-server connect support via `nfs4_pnfs_v3_ds_connect_unload()`,
2. unregisters NFSv4,
3. exits NFSv4.2 xattr cache and unregisters SSC ops if enabled,
4. unregisters sysctl,
5. quits idmap,
6. destroys DNS resolver.

## Cross-File Relationships

- Calls `nfs4_register_sysctl()` and `nfs4_unregister_sysctl()` from `nfs4sysctl.c`.
- Uses NFSv4 state/delegation and pNFS helpers whose recovery behavior is coordinated by `nfs4state.c`.
- Provides module lifetime for tracepoints instantiated in `nfs4trace.c` as part of NFSv4 client support.

## Research Takeaways

`nfs4super.c` is the VFS-facing NFSv4 glue file. Its most important behaviors are NFSv4-specific inode cleanup, pNFS layout commit integration, referral-safe mounting through a root mount plus `mount_subtree()`, and ordered module initialization of resolver, idmap, xattr, sysctl, SSC, and NFS version registration.
