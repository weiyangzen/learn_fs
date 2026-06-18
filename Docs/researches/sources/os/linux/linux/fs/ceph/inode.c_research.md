# File Research: sources/os/linux/linux/fs/ceph/inode.c

## Purpose

`inode.c` is the central CephFS inode implementation. It allocates, initializes, fills, updates, evicts, and shuts down `struct ceph_inode_info` instances and wires CephFS inode state into the Linux VFS inode, dentry, readdir, getattr, setattr, symlink, fscrypt, fscache, quota, snapshot, capability, and MDS reply paths.

The file is primarily responsible for translating authoritative metadata returned by MDS replies into local kernel state while respecting Ceph capability ownership. It also maintains directory fragment routing metadata, dentry leases, readdir cache state, deferred page-cache invalidation/truncation work, and synchronous or local setattr decisions.

## Major Interfaces

- `ceph_new_inode()` preallocates a VFS inode for create-like operations, prepares ACL/security context, and prepares fscrypt context except for snapdir children.
- `ceph_as_ctx_to_req()` transfers prepared ACL/security/fscrypt context into an MDS request.
- `ceph_get_inode()` finds or inserts an inode by Ceph virtual inode number (`struct ceph_vino`), using `iget5_locked()`/`inode_insert5()` and `ceph_ino_compare`.
- `ceph_get_snapdir()` creates or returns the synthetic `.snap` directory inode associated with a real directory.
- `ceph_alloc_inode()`, `ceph_free_inode()`, and `ceph_evict_inode()` implement inode cache lifecycle and cleanup of Ceph-specific state.
- `ceph_fill_inode()` assimilates a parsed MDS inode record into a live inode, including caps, layout, xattrs, size/time, symlink target, directory stats, snapshots, encryption state, and inline data.
- `ceph_fill_trace()` assimilates an MDS reply trace into parent, target inode, and dentry cache state.
- `ceph_readdir_prepopulate()` prepopulates inode/dentry cache and optional page-backed readdir cache from MDS readdir replies.
- `ceph_inode_set_size()` updates size and reports whether size should be sent to the MDS.
- `ceph_queue_inode_work()` schedules deferred inode work on `fsc->inode_wq`.
- `__ceph_do_pending_vmtruncate()` and `ceph_do_invalidate_pages()` perform deferred page-cache truncation and invalidation.
- `__ceph_setattr()` and `ceph_setattr()` implement local-vs-remote setattr logic.
- `__ceph_do_getattr()`, `ceph_getattr()`, `ceph_do_getvxattr()`, and `ceph_permission()` implement metadata refresh and VFS stat/permission behavior.
- `ceph_try_to_choose_auth_mds()` chooses auth MDS for operations that should avoid stale replicas.
- `ceph_inode_shutdown()` purges caps and marks an inode unusable after shutdown.

## Inode Allocation And Identity

`ceph_set_ino_cb()` is the inode-hash initializer callback. It stores the Ceph vino in `ci->i_vino`, maps it to VFS `i_ino`, resets inode versioning, and increments the MDS client's total inode metric. Reserved vino values are rejected in `ceph_get_inode()` with `-EREMOTEIO`.

`ceph_get_reply_dir()` protects reply assimilation from parent-dentry races. If an MDS reply contains directory inode identity that no longer matches `req->r_parent`, it warns once and obtains the correct inode from the cache with `ceph_get_inode()`. Callers must drop the extra reference when it differs from the request parent.

`ceph_get_snapdir()` synthesizes a snapdir inode with the parent's inode number and snap id `CEPH_SNAPDIR`. It copies mode, ownership, timestamps, birth time, and encryption auth from the parent, assigns snapdir inode/file operations, pins it with `CEPH_CAP_PIN`, and unlocks a newly allocated inode. It rejects non-directory parents or cached snapdir inodes with inconsistent type.

## Directory Fragment State

The file maintains per-directory fragment routing in `ci->i_fragtree`, an rb-tree protected by `ci->i_fragtree_mutex`.

- `__get_or_create_frag()` inserts `struct ceph_inode_frag` entries with default MDS delegation state.
- `__ceph_find_frag()` looks up a fragment.
- `__ceph_choose_frag()` walks the fragment split tree to choose the leaf containing a hash value, optionally returning delegation state.
- `ceph_choose_frag()` wraps selection under the fragment-tree mutex.
- `ceph_fill_dirfrag()` updates delegation/referral metadata from an MDS dirfrag record, removing unneeded leaf referrals when the auth MDS matches and `ndist == 0`.
- `ceph_fill_fragtree()` reconciles the split tree from an MDS `ceph_frag_tree_head`, sorting split records when necessary and deleting stale split/leaf nodes.

This code is sensitive to stale routing metadata. It treats allocation failure while recording delegation as non-fatal because inaccurate delegation can be corrected by later MDS interactions, but it logs an error.

## Inode Private State Initialization

`ceph_alloc_inode()` initializes `struct ceph_inode_info` and the embedded netfs inode. It sets default versions, counters, layout state, xattr state, cap trees/lists, wait queues, truncate state, max-size reporting state, per-mode open counts, unsafe operation lists, snap realm state, deferred work, birth time, and optional fscrypt fields.

`ceph_evict_inode()` performs the reverse cleanup:

- waits for outstanding netfs I/O;
- truncates final pages;
- releases fscache usage/cookies;
- clears the VFS inode;
- removes all capabilities;
- adjusts quota realm counters;
- drops snap realm or snapid map references;
- frees all dirfrag tree nodes;
- destroys xattr caches and buffers;
- drops layout pool namespace references.

## MDS Metadata Assimilation

`ceph_fill_inode()` is the core MDS reply assimilation function. It is called with `mdsc->snap_rwsem` held. It handles both new and existing inodes and refuses type or device-number changes after `I_NEW` has cleared.

Important phases:

- Preallocate a cap object when reply caps are present for a non-snapshot inode.
- Preallocate an xattr blob when the reply has real xattr data.
- Intern or reference pool namespace strings.
- Attach snapshot id mapping for snapshot inodes.
- Decide whether the MDS record is a newer authoritative version.
- Update Linux change attribute from `iinfo->change_attr`.
- Compute already issued/dirty caps and newly issued caps.
- Update quota and immutable subvolume id.
- Install fscrypt auth on first encrypted inode observation.
- Update auth metadata only when the client lacks exclusive auth caps or receives newly shared auth caps.
- Update inode block size from fscrypt or Ceph file layout.
- Update link count, times, file/dir counts, file layout, max size, directory rstats, xattrs, and `ci->i_version` according to cap ownership.
- Assign VFS inode operations/file operations by inode type.
- Decode and cache symlink targets, with separate encrypted symlink handling.
- Add newly issued caps or snapshot caps.
- Fill inline data when present and useful.
- Wake cap waiters, queue truncation, update fragment split tree, and update dirfrag delegation.

Size handling is split into `ceph_fill_file_size()`, which honors truncate sequence ordering and capability ownership. It updates `i_size`, `i_blocks`, fscache, reported size, truncate sequence, and `i_truncate_pagecache_size`. It queues deferred VM truncation when the client still holds cache/buffer caps, the mapping is mmaped, or the file is open and page cache must be reconciled later.

Time handling is split into `ceph_fill_file_time()`. With exclusive or write-like caps, local times can be newer than MDS values. The code uses `time_warp_seq` to distinguish explicit utimes/truncate ordering from normal monotonic mtime/atime growth. Without write/exclusive caps, MDS time is accepted when the sequence is not older.

Subvolume handling in `ceph_inode_set_subvolume()` treats non-zero subvolume id as immutable. A later conflicting non-zero id triggers `WARN_ON_ONCE` and is ignored.

## Dentry Lease And Trace Handling

`__update_dentry_lease()` stores MDS lease information in `struct ceph_dentry_info`, including primary-link state, shared generation, session reference, sequence, renew deadlines, and expiry. It only tracks leases for normal non-snapshot directories.

`update_dentry_lease_careful()` is used when the parent inode lock is not held. It validates dentry name, parent vino, and target/negative state before updating the lease.

`splice_dentry()` attaches a dentry to an inode with `d_splice_alias()`. For directories it first finds any existing alias and prunes it so the origin parent's readdir cache does not continue to reference a dentry that will move.

`ceph_fill_trace()` processes MDS replies that can contain a directory inode, a dentry, and/or a target inode. It:

- handles empty replies and invalidates directory request state when appropriate;
- fills the reply directory inode, including the corrected parent lookup path from `ceph_get_reply_dir()`;
- for encrypted lookup-by-name, converts MDS names to user-visible names and builds or finds the correct dentry;
- fills the target inode and unlocks new inodes;
- handles null dentries for unlink/negative lookup;
- handles rename by `d_move()` and lease invalidation;
- splices target inodes into negative dentries;
- handles snapdir lookup/mksnap dentries;
- updates leases carefully when parent locking is absent.

The function is tightly coupled to MDS request flags such as `CEPH_MDS_R_PARENT_LOCKED`, `CEPH_MDS_R_ABORTED`, and `CEPH_MDS_R_ASYNC`. It avoids installing stale dentry bindings when replies are aborted or when identities mismatch.

## Readdir Prepopulation And Cache

`readdir_prepopulate_inodes_only()` fills inode metadata from readdir replies when an MDS request was aborted, but avoids dentry cache changes.

`ceph_readdir_prepopulate()` populates dentries, inodes, dentry offsets, leases, and an optional page-backed readdir cache from `rinfo->dir_entries`. It supports both frag-order and hash-order readdir, tracks offset hash transitions, updates dirfrag metadata, and initializes directory release/ordered counters at the start of a leftmost fragment read.

`fill_readdir_cache()` stores dentry pointers in folios under `dir->i_data` only while the request's release and ordered counters still match the directory. If the directory changes during fill, it disables the cache by setting the control index to `-1`.

The function avoids splicing dentries for security-xattr deadlock cases and marks the request with `CEPH_MDS_R_DID_PREPOPULATE` only when the prepopulation completed without errors or skipped entries.

## Deferred Work, Page Cache, And Truncation

`ceph_queue_inode_work()` sets a bit in `ci->i_work_mask`, takes an inode reference, and queues `ci->i_work` on the Ceph inode workqueue. Duplicate queue attempts drop the extra reference.

`ceph_inode_work()` drains these bits:

- `CEPH_I_WORK_WRITEBACK`: `filemap_fdatawrite()`;
- `CEPH_I_WORK_INVALIDATE_PAGES`: `ceph_do_invalidate_pages()`;
- `CEPH_I_WORK_VMTRUNCATE`: `__ceph_do_pending_vmtruncate()`;
- `CEPH_I_WORK_CHECK_CAPS`: `ceph_check_caps()`;
- `CEPH_I_WORK_FLUSH_SNAPS`: `ceph_flush_snaps()`.

`ceph_do_invalidate_pages()` invalidates fscache and page cache while coordinating with read-cache revocation generation counters. If the inode is shut down, it sets mapping error `-EIO` and truncates all page cache. Successful invalidation decrements `i_rdcache_revoking` and may trigger cap checking.

`__ceph_do_pending_vmtruncate()` serializes truncation under `i_truncate_mutex`, flushes dirty snapped pages before truncating, warns if readers/writers remain, resizes fscache, truncates page cache to `i_truncate_pagecache_size`, clears pending state if stable, checks caps when no write-buffer refs remain, and wakes cap waiters.

## Symlink And Fscrypt Behavior

Encrypted symlink targets are base64 decoded by `decode_encrypted_symlink()` when fscrypt support is enabled; otherwise the operation returns `-EOPNOTSUPP`. Encrypted symlinks use `ceph_encrypted_symlink_iops`, whose `get_link` calls `fscrypt_get_symlink()` on `ci->i_symlink`. Their getattr path wraps `ceph_getattr()` and then applies `fscrypt_symlink_getattr()`.

`fill_fscrypt_truncate()` supports encrypted unaligned shrink truncation. It obtains read caps, writes back dirty cache if buffer caps are issued, reads the last fscrypt block, zeroes bytes after the new EOF, encrypts the block in place, and attaches a `ceph_fscrypt_truncate_size_header` plus block data to the MDS request pagelist. Hole cases send only header metadata. This path exists so the MDS can safely update the encrypted last block while applying truncation.

## Setattr And Getattr

`__ceph_setattr()` decides whether an attribute change can be satisfied locally under held exclusive/write caps or must be sent to the MDS. It may first check MDS path access to avoid locally applying changes that should be denied, falling back to MDS-side auth checks for non-`EACCES` failures.

For uid, gid, mode, atime, mtime, size, and fscrypt auth, it:

- records local dirty caps when exclusive/write caps are sufficient and synchronous MDS validation is not required;
- otherwise fills an MDS setattr request mask and cap-release set;
- updates local ctime and inode version when dirtying caps locally;
- handles ctime-only dirtying by selecting an available exclusive cap or sending a nearly no-op remote setattr;
- performs encrypted truncate RMW setup when shrinking to an unaligned fscrypt block;
- retries encrypted truncate requests that return `-EAGAIN` up to a fixed retry budget;
- runs pending VM truncation after successful remote size changes.

`ceph_setattr()` rejects snapshot writes, shutdown inodes, oversize files, and quota-exceeding size changes. It runs fscrypt and generic setattr preparation, delegates to `__ceph_setattr()`, and updates POSIX ACLs after mode changes.

`__ceph_do_getattr()` checks for sufficient caps unless forced, chooses auth or any MDS, sends `CEPH_MDS_OP_GETATTR`, and has a special locked-page inline-data mode where success returns inline length or `-ENODATA`.

`statx_to_caps()` maps requested statx fields to Ceph cap masks. `ceph_getattr()` optionally refreshes metadata, fills generic attributes, exposes Ceph-presented inode number, birth time, change cookie, snapshot dev id, directory logical size/link count semantics, and encrypted/change-monotonic attributes.

`ceph_permission()` refreshes auth caps before calling `generic_permission()` and refuses nonblocking permission checks with `-ECHILD`.

`ceph_do_getvxattr()` sends `CEPH_MDS_OP_GETVXATTR` to auth MDS with feature bit `CEPHFS_FEATURE_OP_GETVXATTR`, returning size, copying value, or `-ERANGE`.

## Locking And Concurrency

Important locks and ordering:

- `mdsc->snap_rwsem` is required by `ceph_fill_inode()`.
- `ci->i_ceph_lock` protects most inode private counters, caps, flags, xattr blob pointer updates, layout namespace pointer swaps, truncate state, and fscrypt auth installation.
- `ci->i_fragtree_mutex` protects fragment tree mutations and lookup.
- dentry `d_lock` protects dentry lease state.
- `ci->i_truncate_mutex` serializes page-cache invalidation/truncation.
- MDS request fill paths rely on request flags and sometimes parent directory `i_rwsem` for safe dentry binding.

The file is careful to drop `i_ceph_lock` around allocations, symlink decoding, inline data filling, and operations that can sleep. Some paths preallocate cap flushes, caps, xattr buffers, or strings before taking locks to avoid sleeping under spinlocks.

## External Dependencies

This file depends heavily on:

- Ceph MDS client request/session/cap APIs from `mds_client.h` and related CephFS internals;
- VFS inode, dentry, xattr, ACL, statx, permission, symlink, page-cache, and writeback APIs;
- netfs and fscache APIs;
- fscrypt APIs and Ceph fscrypt helpers;
- Ceph wire decode/layout/fragment helpers from `linux/ceph/*`;
- quota, snapshot realm, dir, file, xattr, cap, and cache helpers implemented elsewhere in `fs/ceph`.

## Error Handling And Risks

- MDS reply assimilation is race-prone by design; the code uses version numbers, cap ownership, request flags, and vino checks to avoid stale metadata installation.
- Type or device changes on an existing inode are treated as stale metadata and return `-ESTALE`.
- Directory fragment allocation failure can leave routing metadata inaccurate, but the code continues because correctness can be recovered through MDS routing.
- Encrypted symlink decode allocates `enclen + 1` but writes `sym[declen + 1] = '\0'`; this is notable because normal string termination would be `sym[declen]`. It may be intentional only if decoder behavior leaves a spare byte, but it deserves review in fscrypt symlink tests.
- `fill_fscrypt_truncate()` sets `header.data_len` differently for hole vs data cases, but appends block data when `header.block_size` is nonzero rather than based on object existence. This should be checked against the expected wire format.
- Setattr mixes local optimistic updates with remote MDS requests. Correctness depends on cap ownership and later cap flush behavior.
- Dentry splice and readdir cache updates depend on parent locking assumptions. The careful lease path validates names/vinos before touching unlocked parent-derived state.

## Testing Signals

Relevant tests should exercise:

- MDS reply races with renamed parents and mismatched directory vino.
- Directory fragmentation updates, split-tree pruning, and delegated fragment selection.
- Readdir prepopulation with hash-order replies, changed directory counters, nokey names, and stale positive dentries.
- Local vs remote setattr under different cap combinations.
- Encrypted symlink lookup/getattr and encrypted unaligned shrink truncate.
- Snapdir inode creation and stats.
- Shutdown/eviction while caps, fscache, and page-cache invalidation are active.
