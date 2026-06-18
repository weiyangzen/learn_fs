# File Research: sources/os/linux/linux-stable/fs/fuse/inode.c

## Purpose

`inode.c` implements FUSE module initialization, filesystem registration, superblock setup, mount context parsing, connection setup/teardown, FUSE_INIT negotiation, inode allocation/eviction, attribute installation, export support, syncfs, submounts, and device association.

## Main Responsibilities

- Defines module metadata and module parameters.
- Manages global FUSE connection list and global mutex.
- Allocates and frees FUSE inode cache objects.
- Initializes and releases `struct fuse_conn`, `struct fuse_mount`, and `struct fuse_dev`.
- Implements FUSE inode attribute refresh and inode instantiation.
- Sends FORGET on inode eviction and submount lookup release.
- Implements reverse inode invalidation support.
- Implements superblock operations: alloc/free/evict inode, write inode, statfs, syncfs, show options, umount begin.
- Parses mount options for `fuse` and `fuseblk`.
- Negotiates protocol features with the userspace server through `FUSE_INIT`.
- Registers `fuse` and `fuseblk` filesystem types.
- Initializes `/dev/fuse`, fusectl, sysfs mount point, dentry invalidation work, and sysctls.

## Inode Allocation and Eviction

`fuse_alloc_inode()` allocates `struct fuse_inode` from `fuse_inode_cachep`, clears private fields, initializes locks, allocates a forget message, and optional DAX/passthrough state.

`fuse_evict_inode()`:
- Warns if dirty inode metadata remains.
- Breaks DAX layouts.
- Truncates pages and clears the inode.
- Sends `FORGET` for outstanding lookup references if the superblock is active.
- Releases submount lookup refs.
- Increments `evict_ctr` for non-deleted inodes to invalidate racing lookups.
- Checks that regular-file cache/writeback lists are empty.

## Attribute Handling

`fuse_change_attributes_common()` installs server attributes into the Linux inode while holding `fi->lock`:
- Clears invalid masks when safe.
- Advances attribute version.
- Updates mode, nlink, uid/gid, blocks, times, btime, block size, original mode/ino.
- Preserves sticky-bit semantics when the kernel is not doing default permissions.
- Clears `S_NOSEC` because server-side security metadata may have changed.

`fuse_change_attributes_i()` wraps this with writeback-cache handling:
- Trusts local size/mtime/ctime when writeback cache is active for regular files.
- Ignores stale attribute updates by comparing `attr_version`.
- Avoids applying size changes while `FUSE_I_SIZE_UNSTABLE` is set.
- Truncates or invalidates page cache when size or mtime indicates stale data.
- Applies DAX dont-cache flags.

`fuse_get_cache_mask()` captures the writeback-cache rule: local size, mtime, and ctime can be authoritative for regular files.

## Inode Lookup

`fuse_iget()` creates or finds inodes by FUSE nodeid:
- Handles auto-submount roots specially because their nodeids are not unique within the parent filesystem hash.
- Uses `iget5_locked()` for ordinary inodes.
- Marks stale reused-nodeid inodes bad.
- Initializes inode operation tables by file type.
- Increments `nlookup`.
- Applies attributes and unlocks new inodes.

`fuse_ilookup()` scans all mounts sharing a connection under `fc->killsb` to find a nodeid. It supports notifications and shared-connection submounts.

`fuse_reverse_inval_inode()` handles server-initiated invalidation by nodeid, invalidating attrs, ACLs, and optional page ranges.

## Mount and Superblock Setup

`fuse_parse_param()` handles modern fs_context parameters:
- `source`
- `fd`
- `rootmode`
- `user_id`
- `group_id`
- `default_permissions`
- `allow_other`
- `max_read`
- `blksize`
- `subtype`

It validates `/dev/fuse` file type and user namespace matching.

`fuse_fill_super_common()` initializes the superblock:
- Applies standard FUSE superblock defaults.
- Sets block size for `fuseblk` or page-sized blocks for normal FUSE.
- Allocates DAX connection state if requested.
- Initializes backing device info with strict dirty limits.
- Sets POSIX ACL support and mount options.
- Creates the root inode and root dentry.
- Adds the connection to fusectl and global list.
- Installs the device connection and wakes `/dev/fuse` waiters.

`fuse_get_tree()` creates a new connection/mount pair, supports `fuseblk`, normal nodev mounts, and reusing an already initialized FUSE device connection.

## Submounts

FUSE submounts share a `fuse_conn` but have distinct superblocks:
- `fuse_dentry_automount()` in `dir.c` creates a submount context.
- `fuse_get_tree_submount()` allocates a new `fuse_mount`, shares the parent connection, and creates a superblock rooted at the mountpoint inode.
- `fuse_fill_super_submount()` copies relevant superblock settings, duplicates the root inode, and shares submount lookup accounting so FORGET is delayed until all submount users are gone.

## FUSE_INIT Negotiation

`fuse_send_init()` creates and sends `FUSE_INIT`, synchronously or in background depending on `sync_init`.

`process_init_reply()` validates protocol version, processes background limits, and maps negotiated flags to connection behavior:
- async read/direct I/O,
- POSIX/flock locking,
- atomic truncate,
- export support,
- big writes and max pages,
- dont-mask,
- auto/explicit invalidation,
- readdirplus,
- writeback cache,
- parallel dirops,
- killpriv v1/v2,
- time granularity,
- POSIX ACL/default permissions,
- symlink caching,
- abort error behavior,
- DAX map alignment and inode DAX,
- extended setxattr,
- security context and supplementary group creation,
- direct-I/O mmap allowance,
- passthrough,
- no-export support,
- idmapped mounts,
- io_uring transport,
- request timeout.

It sets max readahead, minor version, max write, and connection initialized/error state.

## Syncfs and Writeback Buckets

When `sync_fs` is enabled:
- `fuse_sync_fs_writes()` switches the current writeback bucket and waits for all writes in the old bucket.
- `fuse_sync_fs()` then sends `FUSE_SYNCFS`, disabling the feature on `-ENOSYS`.

This ensures syncfs sees all FUSE writepages that were in flight before the sync boundary.

## Export Support

NFS/export helpers encode file handles as nodeid/generation pairs, optionally with parent. `fuse_get_dentry()` can reconstruct dentries by inode lookup or server lookup of `"."` when export support is negotiated. `FUSE_NO_EXPORT_SUPPORT` switches to encode-only export operations.

## Device and Connection Lifecycle

`fuse_conn_init()` initializes locks, queues, counters, feature defaults, namespace refs, request limits, random lock-owner scramble key, optional passthrough backing map, and mount list membership.

`fuse_conn_put()` tears down DAX, timeouts, epoch work, input queue ops, pid/user namespaces, sync bucket, backing files, io_uring, and final release via RCU.

`fuse_dev_alloc()`, `fuse_dev_install()`, `fuse_dev_alloc_install()`, and `fuse_dev_put()` allocate processing queues, attach devices to connections, and drop connection refs.

`fuse_conn_destroy()` optionally sends `FUSE_DESTROY`, aborts the connection, waits for abort completion, and removes fusectl/global-list entries.

## Module Initialization

`fuse_init()` performs full module startup:
- initializes global connection list,
- registers `fuse`/`fuseblk`,
- initializes `/dev/fuse`,
- creates sysfs `fs/fuse/connections`,
- initializes fusectl,
- initializes dentry invalidation trees,
- sanitizes background request limits.

`fuse_exit()` reverses those steps.

## Edge Cases and Risks

- Attribute updates must be versioned to avoid applying stale server replies after local changes.
- Eviction races with lookup/readdirplus are handled with `evict_ctr`.
- Mount fd namespace checks are security-critical.
- FUSE_INIT feature combinations matter; passthrough is rejected with writeback cache.
- Submount nodeids are intentionally excluded from the normal inode hash to avoid alias conflicts.
