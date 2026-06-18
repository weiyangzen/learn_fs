# File Research: sources/os/linux/linux/fs/ceph/dir.c

## Role

`dir.c` implements CephFS directory VFS operations and dentry behavior: lookup, readdir, mkdir/mknod/symlink/link/unlink/rename, snapdir handling, directory seek state, dentry lease validation/trimming, dentry cache lifecycle, and directory operation tables.

## Main Interfaces

- File operations: `ceph_dir_fops`, `ceph_snapdir_fops`.
- Inode operations: `ceph_dir_iops`, `ceph_snapdir_iops`.
- Dentry operations: `ceph_dentry_ops`.
- Externally used helpers include `ceph_make_fpos()`, `ceph_handle_snapdir()`, `ceph_finish_lookup()`, `ceph_handle_notrace_create()`, `ceph_trim_dentries()`, `ceph_invalidate_dentry_lease()`, and `ceph_dentry_hash()`.

## Readdir Model

Ceph directory positions encode either fragment/name order or hash order:

- `ceph_make_fpos(high, off, hash_order)` combines fragment/hash and entry offset.
- `HASH_ORDER` marks hash-ordered positions.
- `fpos_frag()`, `fpos_hash()`, `fpos_off()`, and `fpos_cmp()` interpret encoded positions.

`ceph_readdir()` emits `.` and `..`, prepares fscrypt state, touches write fmode for later directory mutations, then tries dcache-backed iteration if:

- the `DCACHE` mount option is enabled,
- `NOASYNCREADDIR` is not set,
- the inode is not a snapdir,
- the directory is complete and ordered,
- and the client holds `CEPH_CAP_FILE_SHARED`.

If dcache iteration fails with `-EAGAIN`, it falls back to MDS `READDIR` or `LSSNAP`.

## Dcache Readdir

- `__dcache_find_get_entry()` locates dentry pointers stored in the directory inode page cache, locking the folio and using RCU plus lockref to safely take a live dentry.
- `__dcache_readdir()` binary-searches the cached dentry pointer array by stored `di->offset`, validates hash/order generation and fscrypt key state, emits entries, touches directory leases, and records the last emitted name.
- Dcache readdir is invalidated when ordered completeness no longer matches release/order counters, entries are missing, negative/unhashed, generation differs, or nokey dentries become decryptable.

## MDS Readdir

When a new chunk is needed, `ceph_readdir()`:

- creates `CEPH_MDS_OP_READDIR` or `CEPH_MDS_OP_LSSNAP`,
- allocates reply buffers,
- sets direct MDS/hash routing for directory fragments,
- encodes the last name for encrypted directories when resuming,
- passes release/order/cache index hints,
- pins the inode and dentry on the request,
- parses reply entries and emits them with `dir_emit()`.

It tracks `dfi->last_readdir`, `dfi->last_name`, `dfi->frag`, `dfi->next_offset`, `dir_release_count`, `dir_ordered_count`, and `readdir_cache_idx`. At the end of all fragments it can mark the directory complete and ordered if no dentries were released and order counters still match.

`ceph_dir_llseek()` supports `SEEK_SET` and `SEEK_CUR`, rejects `SEEK_END`, and resets buffered readdir state when seeking to zero, another fragment, before the current chunk, or across hash/non-hash ordering.

## Lookup and Snapdir Handling

- `ceph_lookup()` handles name length, fscrypt lookup preparation, local negative lookup from complete cached directories, and MDS `LOOKUP`/`LOOKUPSNAP`.
- `ceph_handle_snapdir()` maps the configured hidden snapdir name to `ceph_get_snapdir(parent)` for normal parent directories.
- `ceph_finish_lookup()` normalizes MDS lookup results, including `-ENOENT` without a trace, dentry splicing, and stale positive dentries.
- Root dentries beginning `.ceph` are not concluded locally negative by complete-directory logic.

## Create and Mutation Operations

- `ceph_mknod()` implements mknod and regular create via `ceph_create()`. It rejects non-head snapshots, waits for conflicting async unlink, checks max-files quota, allocates a new inode, sets fscrypt-file flags for encrypted regular files, attaches ACL/security context, and sends `MKNOD`.
- `ceph_symlink()` prepares encrypted symlink targets with fscrypt/base64 when needed, otherwise duplicates the target path, then sends `SYMLINK`.
- `ceph_mkdir()` handles normal `MKDIR` and `.snap/foo` as `MKSNAP`, including snapshot/fscrypt key restrictions and max-files quota.
- `ceph_link()` prepares fscrypt link context, sends `LINK`, drops source link caps, and locally instantiates on traceless success.
- `ceph_unlink()` handles `UNLINK`, `RMDIR`, and `.snap/foo` as `RMSNAP`. It can perform async unlink when `ASYNC_DIROPS` is enabled and the client holds sufficient directory caps.
- `ceph_rename()` supports ordinary rename and snap rename within snapdir, rejects flags, cross-snapshot rename, non-head snapshots, and cross-quota-realm moves.

Mutation requests consistently set dentry cap drop/unless masks so stale shared/auth/xattr/file caps are revoked or preserved according to MDS rules.

## Async Unlink

`get_caps_for_async_unlink()` requires `CEPH_CAP_FILE_EXCL | CEPH_CAP_DIR_UNLINK`, a matching shared generation, and a primary-link dentry. On async submission:

- the dentry is marked `CEPH_DENTRY_ASYNC_UNLINK`,
- added to `fsc->async_unlink_conflict`,
- the target inode is pinned in `req->r_old_inode`,
- and local nlink/dcache state is adjusted on successful submission.

`ceph_async_unlink_cb()` removes conflict tracking, clears the async bit, handles `-EJUKEBOX` specially, and on errors marks parent/target mappings, clears directory completeness, drops the dentry, logs the path, releases the old inode, and releases directory caps.

## Dentry Lease Management

Ceph tracks two lease lists:

- `mdsc->dentry_leases` for direct MDS dentry leases.
- `mdsc->dentry_dir_leases` for directory-wide shared-cap leases.

Important routines:

- `__ceph_dentry_lease_touch()` refreshes direct lease list position.
- `__ceph_dentry_dir_lease_touch()` refreshes directory lease list position while respecting still-valid direct leases.
- `__dentry_lease_is_valid()` validates lease generation and TTL against the session.
- `__dir_lease_try_check()` validates directory lease generation against parent `i_shared_gen` and `CEPH_CAP_FILE_SHARED`.
- `ceph_trim_dentries()` walks both lists, deleting stale leases and optionally expiring dir leases when cap pressure exceeds `caps_use_max`.
- `ceph_invalidate_dentry_lease()` clears lease generation, primary-link state, and unlists the dentry.

The walk logic uses `mdsc->dentry_list_lock`, `dentry->d_lock`, lockref liveness checks, shrink-list staging, and dget/dput to safely dispose unreferenced dentries.

## Dentry Revalidation and Lifecycle

`ceph_d_revalidate()` first delegates fscrypt validation. Snapped dentries and snapdir dentries are trusted. Normal dentries are valid if a direct dentry lease or directory lease is valid and any positive inode still has caps. Otherwise it does an MDS lookup, updates hit/miss metrics, and clears directory completeness if invalid.

`ceph_d_delete()` tells VFS to delete unused positive non-snapped dentries without valid leases. `ceph_d_release()` removes lease list membership, drops lease session references, decrements total-dentry metric, and frees `ceph_dentry_info`. `ceph_d_prune()` clears directory completeness/order when pruning can invalidate dcache readdir assumptions.

## Directory Read Hack and Hashing

`ceph_read_dir()` supports reading directory statistics as text only when mounted with `-o dirstat`; otherwise it returns `-EISDIR`. `ceph_dentry_hash()` returns either the VFS name hash or a Ceph layout-specific string hash for MDS directory partitioning and export support.

## Concurrency and Error Handling

- Directory mutations wait for conflicting async unlink on target dentries.
- Parent `i_rwsem` is assumed for several VFS operations and is marked via `CEPH_MDS_R_PARENT_LOCKED`.
- `i_ceph_lock` protects inode cap/shared-generation/completeness state.
- `dentry->d_lock` protects dentry lease fields, d_parent stability, and dentry-local flags.
- MDS request allocation and reply traces drive VFS dentry instantiation/splicing; traceless create replies are repaired with follow-up lookup where possible.
- Snapshot directories are mostly read-only except explicit snap create/remove/rename operations.
