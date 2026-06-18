# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4_stub_vnops.c

## Purpose

`nfs4_stub_vnops.c` implements NFSv4 client-side vnode operations for trigger stub vnodes used by ephemeral mounts, especially NFSv4 mirror mounts and referrals. A stub vnode represents a directory that should be covered by a new NFSv4 mount when accessed. The file detects trigger operations, constructs mount arguments from parent NFS mount state plus mirror/referral-specific location data, performs the kernel mount, records the mount in an ephemeral tree, and later unmounts idle ephemeral mounts through a per-zone harvester.

## Vnode Operation Surface

The file defines `nfs4_trigger_vnodeops_template`, installed as `nfs4_trigger_vnodeops`, for stub vnodes.

Triggering operations include `open`, `getattr` when `ATTR_TRIGGER` is present, `setattr`, `access`, `lookup`, `create`, `remove`, `link`, `rename`, `mkdir`, `rmdir`, `symlink`, and `readlink`. Most call `nfs4_trigger_mount()` and then reissue the requested VOP on the root vnode of the covering filesystem.

Some operations deliberately do not trigger:

- `getattr` without `ATTR_TRIGGER` returns real NFSv4 attributes for mirror-mount stubs, and fabricated directory attributes for referral stubs through `nfs4_fake_attrs()`.
- `lookup("..")` is special. Mirror mounts call regular `nfs4_lookup()` on the stub, while referrals return the parent vnode via `vtodv()`.
- `inactive`, `rwlock`, `rwunlock`, `fid`, `realvp`, `getsecattr`, and `pathconf` use regular NFSv4 vnodeops because they should not mount.
- `frlock`, `dispose`, and `shrlock` are mapped to `fs_error`.

`nfs4_trigger_rename()` also blocks cross-filesystem semantics early: if source and target directories are different stubs, it returns `EXDEV` without triggering either mount.

## Mount Trigger Flow

`nfs4_trigger_mount()` is the central path.

1. It first calls `nfs4_trigger_mounted_already()` under vnode vfs locks. If another thread already mounted over the stub, it returns the covering root vnode and refreshes the ephemeral reference time.
2. It obtains per-zone trigger globals from `nfs4_ephemeral_key`.
3. It creates or joins the parent mount's `nfs4_ephemeral_tree_t`. Creation links the tree into the zone forest, marks it building, holds the parent `mntinfo4_t` and VFS, and locks the tree. Joining holds the tree and refuses to proceed when tree processing/teardown is underway.
4. It marks the tree mounting, builds mount arguments via `nfs4_trigger_domount_args_create()`, temporarily grants zone privileges to duplicated caller credentials, and calls `nfs4_trigger_domount()`.
5. It clears mounting/building status and releases tree references/locks according to whether this thread created the tree.

The returned vnode is held for the caller. Trigger vnodeops release it after reissuing the real VOP, except `open`, which replaces the caller's stub vnode reference with the new root vnode and delegates to `VOP_OPEN()`.

## Mount Argument Construction

`nfs4_trigger_domount_args_create()` builds a `domount_args_t` containing:

- `ephemeral_servinfo_t` for the server actually used by the mount.
- A comma-separated host list for NFS read-only failover.
- A linked list of `struct nfs_args`, one per responsive server.

It pings the current server first, then iterates all parent `servinfo4_t` entries. Nonresponsive servers are omitted from the failover list. If all servers are down, it sleeps and retries until one responds, unless interrupted. This avoids known mount-path hangs when an unavailable server is passed into the mount code.

`nfs4_trigger_nargs_create()` copies generic mount behavior from the parent `mntinfo4_t` and `servinfo4_t`: soft/hard, interruptible, caching timers, rsize/wsize, timeout/retransmit, local lock/direct I/O/nocto/grpid/public options, security data, and NFSv4 argument extension B. It adjusts referrals to use security negotiation with an AUTH_SYS starting point and to prefer RDMA negotiation (`TRYRDMA` not `DORDMA`). Mirror mounts preserve parent security negotiation policy.

`nfs4_trigger_domount()` constructs the effective mount point from the parent VFS mountpoint plus the stub path, strips zone root prefixes for non-global zones, builds the `hostlist:path` spec, creates an option string, and calls `domount()` with `MS_SYSSPACE | MS_DATA | MS_OPTIONSTR`. On `EBUSY`, it retries once and checks whether another thread won the race by mounting over the stub.

## Mirror Mount Handling

`nfs4_trigger_esi_create_mirrormount()` builds ephemeral server info by deep-copying the selected parent `servinfo4_t`: hostname, address, knetconfig, optional AUTH_DH sync address and netname, and a composed remote path. The remote path combines the parent server path with the stub's path from `fn_path()`, taking care not to produce malformed paths when the parent path is `/`. The copied data is intentionally independent because the new ephemeral mount may outlive or be unmounted separately from the parent structures.

## Referral Handling

Referral support uses several stages:

- `nfs4_fetch_locations()` sends an NFSv4 compound `CPUTFH`, `CLOOKUP`, `GETATTR` requesting `FATTR4_FSID`, `FATTR4_FS_LOCATIONS`, and `FATTR4_MOUNTED_ON_FILEID`. It validates the result and returns `nfs4_ga_res_t` plus the XDR compound result for later cleanup.
- `find_referral_stubvp()` uses `mounted_on_fileid` and the parent directory filehandle to construct a synthetic shared filehandle, creates or finds an NFSv4 vnode with `makenfs4node()`, marks it as a directory, and returns a referral stub vnode.
- `nfs4_setup_referral()` marks that vnode's rnode as a referral stub and enters it in the DNLC.
- `nfs4_process_referral()` fetches fs_locations, detects migration by checking whether the fsid already exists in the rnode cache, resolves candidate servers through `nfs4_callmapid()`, and selects the first server responding to an NFSv4 NULL ping.
- `nfs4_trigger_esi_create_referral()` fetches the parent directory/name, calls `nfs4_process_referral()`, then builds `ephemeral_servinfo_t` from the selected fs_location rootpath and resolved network data.

The mapid upcall in `nfs4_callmapid()` uses the zone's nfsmapid door with XDR-encoded `NFSMAPID_SRV_NETINFO`, handles missing daemon cases, and decodes `struct nfs_fsl_info`.

## Ephemeral Mount Tree Model

Each zone owns `nfs4_trigger_globals_t`, containing a forest lock, current mount timeout, a harvester-started flag, and a list of `nfs4_ephemeral_tree_t` roots. Each tree tracks:

- Tree-wide locks and reference count.
- Status bits for building, mounting, processing, unmounting, derooting, invalid, and harvester-locked states.
- The non-ephemeral enclosing parent `mntinfo4_t`.
- A root list of `nfs4_ephemeral_t` nodes.

Each ephemeral mount node tracks its `mntinfo4_t`, reference time, timeout copy, child pointer, peer pointer, prior pointer, and traversal/error state.

`nfs4_record_ephemeral_mount()` is called from `nfs4_mount()` after an ephemeral mount succeeds. It starts the harvester if needed, attaches the new `mntinfo4_t` to the parent tree, allocates an ephemeral node, holds the mount and VFS, records the timeout and reference time, and links the node as a child, peer, or tree root depending on whether the parent is itself ephemeral.

## Unmount and Harvesting

Manual and automatic unmounting share the same tree data structures.

- `nfs4_ephemeral_umount()` is called from NFSv4 unmount handling. It detects whether the current mount is an ephemeral node or the enclosing tree root, coordinates with active harvester or recursive unmount work, marks tree status, and either unmounts children of a node or deroots the entire tree.
- `nfs4_ephemeral_unmount_engine()` avoids recursive C stack traversal by iteratively walking to child/peer leaves, setting `MI4_EPHEMERAL_RECURSED`, calling `umount2_engine()`, and stitching tree links after successful unmounts.
- `nfs4_ephemeral_umount_activate()` finalizes node removal after the ordinary unmount path proves the mount is not busy. It unlinks the node, releases tree/mount/VFS references, frees the node, and unlocks the tree.
- `nfs4_ephemeral_harvest_forest()` scans every tree in a zone. It can force-unmount during zone destruction, or time-check nodes against `ne_mount_to` during normal harvests. It walks child/peer relationships without C recursion, records child/peer errors so parents are not removed incorrectly, and frees invalid trees whose refcount reaches zero.
- `nfs4_ephemeral_harvester()` is a per-zone zthread that wakes every `nfs4_trigger_thread_timer` seconds, exits when the zone shuts down, and harvests idle ephemeral mounts only when the forest is non-empty.
- Zone key callbacks allocate per-zone globals, gracefully harvest on zone shutdown, force harvest on zone destroy, and free locks/globals.

The public initialization/teardown entry points are `nfs4_ephemeral_init()` and `nfs4_ephemeral_fini()`. `nfs4_ephemeral_set_mount_to()` updates the per-zone timeout used by future ephemeral mounts.

## Mount Options and Server Ping Helpers

`nfs4_trigger_create_mntopts()` walks the NFSv4 mount option prototype list and appends currently set options from the parent VFS to a comma-separated string, also explicitly handling `xattr`/`noxattr` because those are not in the v4 option prototype list. `nfs4_trigger_add_mntopt()` bounds the string at `MAX_MNTOPT_STR` and returns `EOVERFLOW` if it would exceed the fixed buffer.

`nfs4_ping_server_common()` creates a temporary RPC client for `NFS_PROGRAM` version 4 and sends an `RFS_NULL` call with a two-second timeout and one retry. `nfs4_trigger_ping_server()` wraps it for `servinfo4_t`.

## Dependencies and Integration Points

- VFS/vnode interfaces: vnodeops registration, `domount()`, `VFS_ROOT`, `vn_mountedvfs`, `vn_vfsrlock_wait`, `umount2_engine`, VFS mount options, and vnode references.
- NFSv4 client internals: `mntinfo4_t`, `servinfo4_t`, `rnode4_t`, shared filehandles, recovery locks, security negotiation data, `nfs4_mount()`, `nfs4_lookup()`, `makenfs4node()`, `sfh4_put()`, and rnode cache lookup by fsid.
- RPC and idmap infrastructure: TLI RPC client creation, nfsmapid door upcalls, XDR encode/decode, `struct nfs_fsl_info`.
- Zone infrastructure: zone-specific data keys, zone shutdown detection, zthreads, non-global-zone mountpoint path handling.
- DTrace probes instrument referral fetch/upcall/debug and ephemeral tree derooting.

## Concurrency and Locking Notes

The file uses several layers of synchronization: parent `mi_lock`, tree `net_tree_lock`, tree `net_cnt_lock`, zone forest lock, server info rwlocks, recovery locks, and vnode VFS locks. The mount path avoids duplicate mounts by first checking the covering VFS, then serializing tree creation/building/mounting. The unmount path carefully distinguishes manual unmount, recursive unmount, harvester work, and derooting so that tree invalidation and node finalization happen in the right phase.

## Risks and Edge Cases

- `nfs4_trigger_domount_args_create()` can retry forever when no server responds unless interrupted; this is intended to avoid mounting with an all-dead failover list, but it can stall a caller on persistent outage.
- Referral mount creation depends on the nfsmapid daemon. Missing daemon or malformed XDR responses cause referral setup failure.
- Several routines allocate while holding server or mount locks to deep-copy mutable structures; this avoids stale data but can sleep under locks.
- The ephemeral tree logic is complex and status-bit driven. Bugs in refcount/status transitions could produce busy mounts, leaked tree nodes, or failed automatic cleanup.
- The fixed mount option buffer requires careful option length accounting; overflow is handled by failing mount option creation.
- Referral rootpath construction rejects paths exceeding `MAXPATHLEN`, but the error path must free several partially populated nested allocations.

## Testing and Verification Signals

Useful tests include mirror mount trigger through each vnodeop, lookup of `..` for mirror and referral stubs, concurrent triggers racing on the same stub, failover host-list filtering with one or more unavailable servers, referral resolution via nfsmapid, migration-vs-referral fsid detection, non-global-zone mountpoint path construction, option propagation including xattr/noxattr, harvester timeout unmount, manual unmount of child and enclosing parent trees, forced zone-destroy cleanup, and `EBUSY`/race behavior in `domount()`.
