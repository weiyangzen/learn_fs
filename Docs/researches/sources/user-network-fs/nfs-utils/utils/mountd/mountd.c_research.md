<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/mountd.c -->
# sources/user-network-fs/nfs-utils/utils/mountd/mountd.c

## Purpose

`mountd.c` implements the `rpc.mountd` daemon: it authenticates NFS mount protocol requests, returns export root file handles, lists exports and mounts, manages daemon configuration, creates RPC listeners, and runs worker processes for kernel export cache upcalls.

## Important APIs, types, and functions

Service handlers include `mount_null_1_svc`, `mount_mnt_1_svc`, `mount_mnt_3_svc`, `mount_dump_1_svc`, `mount_umnt_1_svc`, `mount_umntall_1_svc`, `mount_export_1_svc`, `mount_exportall_1_svc`, and `mount_pathconf_2_svc`. Core helpers are `get_rootfh`, `set_authflavors`, `get_exportlist`, `read_mountd_conf`, `killer`, and `main`. Globals control reverse DNS, gid management, netlink, root credential application, cache address mode, HA callouts, thread count, port, descriptors, and enabled NFS versions.

## Control flow

Startup reads `nfs.conf`, parses command-line overrides, sets state paths for `etab` and `rmtab`, adjusts file descriptor limits, unregisters stale RPC registrations, creates MOUNT v1/v2/v3 listeners as configured, daemonizes if requested, opens cache channels, forks cache workers, initializes nfsd path and v4 client support, and enters `my_svc_run`. MNT requests resolve and authenticate the requested path, verify mountpoint constraints, optionally perform subpath lookup under client credentials, cache the export in the kernel, fetch a filehandle, add an rmtab entry, and return success. Export-list requests build a cached RPC export list from authenticated export structures.

## State and persistence behavior

Runtime state includes export cache state, worker processes, listener registrations, and static cached export lists keyed by auth reload counter. Persistent files include `etab` and `rmtab` under the configured state directory. Signal cleanup unregisters RPC services, removes lock files, and frees state path names.

## Dependencies and integration points

It depends on export authentication (`auth_reload`, `auth_authenticate`), kernel export cache helpers (`cache_export`, `cache_get_filehandle`, `cache_open`, `cache_fork_workers`), `nfsd_path` wrappers, credential helpers, config parsing, rpcmisc listener creation, and `rmtab.c`. It integrates with clients through MOUNT RPC and with the kernel nfsd export cache through support library channels.

## Risks and edge cases

Path handling is security-sensitive: symlink resolution, export path races, subpath credential checks, mountpoint enforcement, and crossmount checks all affect access. `get_exportlist` caches static RPC list memory and relies on auth reload counters. Multiworker signal handling kills process groups and waits for cache workers. Listener creation can silently produce no v2/v3 listeners except for a warning. Applying root credentials changes lookup semantics for subpaths.

## Test signals

Integration tests should cover authenticated/denied MNT v1/v3, filehandle sizes, subpath lookup with and without managed gids, crossmount denial, unmounted export rejection, PATHCONF authorization, export list pruning, rmtab add/remove, daemon foreground/background modes, version enable/disable flags, no-listener warnings, and signal cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-utils/utils/mountd/mountd.c -->
