# File Research: sources/os/linux/linux-stable/fs/ceph/inode.c

## Role

`inode.c` is the main CephFS inode metadata integration layer. It allocates and tears down Ceph inodes, maps MDS reply metadata into VFS inode state, manages directory fragmentation/delegation caches, handles dentry lease updates, prepopulates lookup/readdir results, implements setattr/getattr/permission paths, and schedules deferred inode work such as page invalidation, writeback, snap flushing, capability checks, and VM truncation.

## Major Responsibilities

- Create, locate, initialize, and evict Ceph inodes keyed by `ceph_vino`.
- Maintain Ceph-specific inode state in `struct ceph_inode_info`, including caps, xattrs, frag tree, layouts, quotas, snap realms, truncation state, and fscrypt metadata.
- Assimilate MDS inode/dentry/readdir replies into the local dcache/icache.
- Update inode size/time/link/auth/xattr/layout fields only when capabilities and version sequencing permit.
- Implement VFS inode operations for regular files, symlinks, encrypted symlinks, permissions, getattr, and setattr.
- Coordinate local page cache truncation and invalidation after remote metadata changes.
- Track directory fragmentation and delegated/repeated dirfrag routing state.
- Support CephFS snapshots and virtual snapdir inodes.

## Inode Creation And Lookup

`ceph_set_ino_cb()` initializes a newly inserted inode’s Ceph vino, Linux `i_ino`, raw i_version, and increments `mdsc->metric.total_inodes`.

`ceph_get_inode()` is the central inode-cache lookup/insert helper. It rejects reserved vinos, uses `inode_insert5()` when a preallocated inode is supplied, otherwise `iget5_locked()`, and consumes `newino` when another inode wins the race.

`ceph_new_inode()` allocates an inode before create-like operations, sets `CEPH_FSCRYPT_BLOCK_SHIFT`, prepares inherited ACL/security context for non-symlinks, initializes security context, and prepares fscrypt context unless the parent is the virtual snapdir.

`ceph_get_snapdir()` constructs the virtual `.snap` directory inode for a directory. It mirrors mode/owner/timestamps from the parent, borrows fscrypt auth when encrypted, sets snapdir inode ops/file ops, and gives it `CEPH_CAP_PIN` so it can be opened.

## Allocation And Eviction

`ceph_alloc_inode()` allocates `struct ceph_inode_info` from `ceph_inode_cachep`, initializes netfs state, locks, counters, cap state, xattr bookkeeping, snap state, frag tree, truncation fields, max-size fields, mode reference counters, unsafe op lists, work item state, and fscrypt fields.

`ceph_free_inode()` frees symlink and fscrypt-auth buffers, releases fscrypt inode info, and returns the inode object to the slab cache.

`ceph_evict_inode()` waits for outstanding netfs I/O, truncates page cache, clears inode state, unregisters fscache, removes caps, adjusts quota realm accounting, drops snap realm/snapid references, frees all directory frag tree nodes, destroys xattrs, releases xattr blobs, and puts layout pool namespace strings.

## Directory Fragment Tree

CephFS directories can be split into fragments and delegated/replicated across MDS ranks. This file tracks that in `ci->i_fragtree`.

Key helpers:

- `__get_or_create_frag()` inserts a `ceph_inode_frag` into an RB tree keyed by frag id.
- `__ceph_find_frag()` searches the RB tree.
- `__ceph_choose_frag()` walks split nodes to choose the leaf containing a hash value and optionally returns delegation info.
- `ceph_choose_frag()` wraps selection with `i_fragtree_mutex`.
- `ceph_fill_dirfrag()` updates per-fragment auth/replica delegation info from an MDS reply.
- `ceph_fill_fragtree()` reconciles the local split tree with the MDS-provided `ceph_frag_tree_head`, including sorting split records and pruning stale nodes.

Concurrency is split between `i_fragtree_mutex` for frag tree topology and `i_ceph_lock` for cap/auth state reads needed to resolve parent-auth delegation.

## MDS Inode Reply Assimilation

`ceph_fill_inode()` is the largest and most important function in the file. It populates a new or existing inode from `ceph_mds_reply_info_in`.

Important behavior:

- Verifies that an existing inode does not change file type or special-device rdev.
- Preallocates caps, xattr blobs, pool namespace strings, and snapid maps before taking `i_ceph_lock`.
- Decides whether reply metadata is newer using Ceph’s projected/stable inode version semantics.
- Updates raw inode change attribute from `iinfo->change_attr`.
- Merges issued and dirty caps to decide what local state must not be overwritten.
- Updates quota and immutable subvolume id.
- Applies fscrypt auth on new or previously unauthenticated encrypted inodes.
- Updates auth metadata, birth time, snapshot birth time, link count, file times, file counts, layout, pool namespace, file size, max size, directory recursive stats, xattrs, and inode version according to cap ownership.
- Handles encrypted file size by comparing object-rounded size with fscrypt cleartext file length.
- Sets VFS inode operations/file operations by file type.
- Allocates/caches symlink targets, with separate encrypted symlink handling via base64 decode and fscrypt get-link support.
- Adds new caps via `ceph_add_cap()` or accumulates snap caps for snapshot inodes.
- Updates fmode tracking, registers fscache cookies, fills inline data, wakes cap waiters, queues VM truncation, updates frag tree and dirfrag delegation.

The function is careful to avoid overwriting locally authoritative fields when exclusive caps or dirty caps are held.

## Size, Time, Subvolume, And Fscrypt

`ceph_fill_file_size()` applies MDS size/truncate state. It updates `i_size`, `i_blocks`, fscache size, reported size, truncate sequence, and page-cache truncation target. It queues truncation when caps or mappings mean local cached pages may remain beyond the new size. Encrypted files track a separate page-cache truncate size because object size can be rounded to fscrypt block boundaries.

`ceph_fill_file_time()` updates ctime/mtime/atime using capability-sensitive rules. With write/excl caps, it only accepts newer or compatible MDS time data; without relevant caps, MDS timestamps are authoritative.

`ceph_inode_set_subvolume()` sets the inode’s immutable subvolume id once. A later change triggers `WARN_ON_ONCE()` and is ignored.

`fill_fscrypt_truncate()` supports encrypted truncation that cuts through the last encrypted block. It obtains read caps, writes back dirty buffered data if needed, reads the last block, zeroes the truncated tail, encrypts the block in place, and attaches a pagelist payload to the setattr MDS request.

## Dentry And Trace Filling

`ceph_get_reply_dir()` validates that the parent inode associated with a dentry reply matches the directory inode in the reply. If the request parent is stale, it warns once and looks up the correct inode by vino.

Dentry lease helpers:

- `__update_dentry_lease()` updates a dentry lease under session mutex and dentry lock, including primary-link flag, shared generation, TTL, renewal timing, sequence, and session reference.
- `update_dentry_lease()` wraps locking and releases any displaced session.
- `update_dentry_lease_careful()` validates dentry name, parent vino, and target vino before updating leases when the parent inode is not locked.

`splice_dentry()` attaches a dentry to an inode with `d_splice_alias()`. For directories it first prunes any existing alias to prevent stale readdir-cache references after alias movement.

`ceph_fill_trace()` incorporates MDS replies for lookups and mutations. It can fill a parent directory inode, target inode, dentry lease, rename movement, null dentry after unlink/negative lookup, snapped directory lookup, and careful lease-only updates when parent locking is unavailable. It also handles aborted requests and ensures extra parent references from `ceph_get_reply_dir()` are dropped.

## Readdir Prepopulation

`readdir_prepopulate_inodes_only()` fills inode cache entries from readdir replies without dentry manipulation when a request is aborted.

`ceph_readdir_prepopulate()` builds dentries and inodes from directory listing replies, handles hash-ordered offsets, updates dirfrag delegation, starts readdir cache population at the leftmost fragment, resolves stale positive dentries pointing at wrong inos, handles `DCACHE_NOKEY_NAME`, fills inodes, splices negative dentries, sets dentry offsets, updates leases, and records cache entries when ordered/release counts match.

`fill_readdir_cache()` stores dentry pointers in folios under the directory mapping. It disables cache population if directory release/order counters no longer match the request snapshot.

`ceph_readdir_cache_release()` releases the mapped folio used during cache population.

## Deferred Inode Work

`ceph_queue_inode_work()` sets a work bit, takes an inode reference, and queues `ci->i_work` on `fsc->inode_wq`.

`ceph_inode_work()` processes work bits:

- `CEPH_I_WORK_WRITEBACK`: `filemap_fdatawrite()`.
- `CEPH_I_WORK_INVALIDATE_PAGES`: `ceph_do_invalidate_pages()`.
- `CEPH_I_WORK_VMTRUNCATE`: `__ceph_do_pending_vmtruncate()`.
- `CEPH_I_WORK_CHECK_CAPS`: `ceph_check_caps()`.
- `CEPH_I_WORK_FLUSH_SNAPS`: `ceph_flush_snaps()`.

`ceph_do_invalidate_pages()` invalidates fscache and page cache while coordinating with read-cache revocation generation. Shutdown inodes get mapping error `-EIO` and full page-cache truncation.

`__ceph_do_pending_vmtruncate()` applies pending page-cache truncation, flushing dirty snapped pages first when required, resizing fscache, truncating page cache, clearing pending state, checking caps when no write-buffer refs remain, and waking cap waiters.

## Setattr Path

`ceph_setattr()` is the VFS entry point. It rejects snapshots as read-only, rejects shutdown inodes, runs fscrypt and VFS setattr preparation, checks max file size and quota, delegates to `__ceph_setattr()`, then runs `posix_acl_chmod()` after successful mode changes.

`__ceph_setattr()` decides whether requested changes can be applied locally under held exclusive/write caps or must be sent to the MDS. It handles fscrypt auth, uid, gid, mode, atime, mtime, size, ctime-only updates, dirty cap marking, cap release masks, remote setattr requests, encrypted truncate payloads, and retry on `-EAGAIN` for fscrypt RMW races.

Local changes dirty caps and increment raw inode version; remote changes populate `req->r_args.setattr` and drop relevant caps. Size changes that go remote trigger pending VM truncation after success.

## Getattr, Permission, And Virtual Xattrs

`ceph_try_to_choose_auth_mds()` chooses auth MDS instead of a random replica when exclusive caps or rstat/xattr semantics make replica answers expensive or potentially stale.

`__ceph_do_getattr()` checks whether needed caps are already held unless forced; otherwise sends `CEPH_MDS_OP_GETATTR`. With a locked page it validates inline-data reply semantics and returns inline length or `-ENODATA`.

`ceph_do_getvxattr()` sends `CEPH_MDS_OP_GETVXATTR` with `CEPHFS_FEATURE_OP_GETVXATTR`, copies the returned value if the caller buffer is large enough, and returns length or error.

`ceph_permission()` fetches auth-shared metadata before calling `generic_permission()`; nonblocking permission checks return `-ECHILD`.

`statx_to_caps()` maps requested statx fields to Ceph cap masks.

`ceph_getattr()` optionally refreshes metadata, fills generic stats, reports Ceph-present inode number, btime, change cookie, snapshot-specific device id, directory size semantics, snapdir size from snap realm, directory block/nlink adjustments, and statx attributes for monotonic change and encryption.

## Shutdown

`ceph_inode_shutdown()` marks the inode shutdown, purges all inode caps, queues page invalidation if needed, and drops any inode references returned by cap purge.

## Key Interactions

- Depends heavily on `mds_client.h` request/reply/cap machinery.
- Uses `cache.h` for dentry lease and directory cache helpers.
- Uses `crypto.h` and fscrypt APIs for encrypted filenames, symlinks, file sizes, and truncation payloads.
- Uses fscache and netfs helpers for cached data lifecycle.
- Exposes inode operations consumed by other CephFS VFS operation tables.

## Concurrency Notes

- `ci->i_ceph_lock` protects most Ceph inode metadata and cap state.
- `mdsc->snap_rwsem` must be held by `ceph_fill_inode()` callers.
- `i_fragtree_mutex` protects directory fragment tree structure.
- `i_truncate_mutex` serializes page invalidation and VM truncation.
- Dentry leases require `dentry->d_lock`, with session refs managed carefully when lease ownership changes.
- Workqueue operations hold inode refs while queued and release them after work completes.

## Edge Cases And Defensive Checks

- Reserved vinos return `-EREMOTEIO`.
- Existing inode type/rdev changes are treated as stale metadata.
- Directory nonzero file sizes are warned and coerced to zero.
- Subvolume id changes after first set warn and are ignored.
- Parent/directory reply mismatch warns and retries with the correct inode.
- Snapdir and snapshot inodes have special capability, device, and readonly handling.
- Encrypted file size/truncate logic accounts for object-rounded sizes and block RMW requirements.
