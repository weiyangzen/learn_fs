# File Research: sources/os/linux/linux-stable/fs/ceph/dir.c

## Purpose

`dir.c` implements CephFS directory and dentry VFS behavior: readdir, lookup, create-like operations, link/unlink/rename, snapdir handling, dentry lease validation, dcache readdir acceleration, async unlink, and directory operation tables.

## Main Responsibilities

- Implements `ceph_dir_fops`, `ceph_snapdir_fops`, `ceph_dir_iops`, `ceph_snapdir_iops`, and `ceph_dentry_ops`.
- Maintains Ceph-specific dentry state through `ceph_d_init()` and `ceph_d_release()`.
- Encodes and compares readdir positions for fragmented directories and hash-ordered replies.
- Serves readdir from dcache when a directory is complete and protected by shared file caps.
- Falls back to MDS `READDIR`/`LSSNAP` requests when cached directory state is incomplete or invalid.
- Handles lookup, snapdir aliasing, and negative dentry completion.
- Implements metadata mutations: mknod/create, symlink, mkdir/snapshot creation, hard link, unlink/rmdir/snapshot removal, and rename/snapshot rename.
- Manages dentry and directory-wide leases, including renewal, trimming, invalidation, revalidation, and pruning.
- Provides optional `-o dirstat` directory read output.
- Computes directory-entry hashes according to Ceph directory layout.

## Readdir Model

Readdir positions pack directory fragment/hash state into `loff_t`:
- `ceph_make_fpos()` combines a high value and per-fragment offset.
- `HASH_ORDER` marks hash-ordered positions.
- `fpos_frag()`, `fpos_hash()`, and `fpos_off()` decode positions.
- `fpos_cmp()` orders positions using `ceph_frag_compare()` and the low offset.

`ceph_readdir()` always emits `.` and `..` first, then:
- Prepares fscrypt readdir state, clearing complete directory state if unlocking changes visible names.
- Tries `__dcache_readdir()` when mount options and caps prove the directory cache is complete and ordered.
- Sends MDS `READDIR` or `LSSNAP` requests by fragment when cache use is not possible.
- Tracks the last emitted name and next offset so readdir can resume robustly across directory changes.
- Updates `dfi->last_readdir`, `frag`, `next_offset`, `readdir_cache_idx`, release counts, and ordered counts.
- Marks a directory complete/ordered when the full traversal completes without dentry releases or ordering changes.

## Dcache Readdir

`__dcache_readdir()` reads cached dentry pointers from the directory inode mapping:
- Uses `__dcache_find_get_entry()` to locate cached dentries by index.
- Binary-searches to the requested position when possible.
- Rejects unhashed, negative, stale-generation, or now-decryptable nokey dentries.
- Touches directory leases before emitting entries.
- Falls back with `-EAGAIN` if cached content is missing or inconsistent.

The directory inode `i_size` is used as the number of cached dentry pointer entries when the directory is complete and ordered.

## Lookup and Snapdir Handling

`ceph_lookup()`:
- Rejects overlong names.
- Prepares encrypted partial lookup when needed.
- Can answer local `-ENOENT` from a complete cached directory, excluding snapdir and root `.ceph*` special cases.
- Otherwise sends `LOOKUP` or `LOOKUPSNAP` to an MDS.
- Requests inode/auth/xattr caps needed for VFS/security behavior.

`ceph_handle_snapdir()` splices the synthetic `.snap` directory when an MDS returns `-ENOENT` for the configured snapdir name under a head directory.

`ceph_finish_lookup()` handles traceless `-ENOENT`, spliced dentries, and VFS return conventions.

## Create, Link, Unlink, and Rename

Mutation operations are translated into MDS requests:
- `ceph_mknod()` and `ceph_create()` send `MKNOD`; regular files under encrypted directories set the fscrypt file request bit.
- `ceph_symlink()` encrypts symlink targets when the new symlink inode is encrypted, then sends `SYMLINK`.
- `ceph_mkdir()` sends `MKDIR` or `MKSNAP` for `.snap/name`.
- `ceph_link()` sends `LINK` and may instantiate the new dentry locally if the reply has no trace.
- `ceph_unlink()` sends `UNLINK`, `RMDIR`, or `RMSNAP`.
- `ceph_rename()` sends `RENAME` or `RENAMESNAP`, disallowing unsupported flags, cross-snapshot renames, and cross-quota renames.

Common behavior:
- Snapshot trees are read-only except snapdir snapshot creation/removal/rename operations.
- Quota checks reject max-files violations before create/mkdir/symlink.
- `ceph_wait_on_conflict_unlink()` serializes against conflicting async unlink.
- fscrypt helpers validate link/rename compatibility.
- Dentry cap drops and “unless” masks tell the MDS what cached state can be revoked.
- `ceph_handle_notrace_create()` follows old-MDS traceless create replies with a lookup.

## Async Unlink

When `ASYNC_DIROPS` is enabled, `ceph_unlink()` can submit async unlink for regular unlink:
- `get_caps_for_async_unlink()` requires directory `FILE_EXCL | DIR_UNLINK` caps, matching shared generation, and primary linkage.
- The dentry is marked `CEPH_DENTRY_ASYNC_UNLINK` and inserted into `async_unlink_conflict`.
- On successful submission, local link count and dcache state are updated optimistically.
- `ceph_async_unlink_cb()` removes conflict tracking, wakes waiters, handles `-EJUKEBOX` retry fallback, and marks parent/target mappings on real failure.

## Dentry Lease System

Two lease concepts are maintained:
- Per-dentry MDS leases, tracked by `lease_gen`, `lease_session`, `lease_seq`, expiry time, and renewal time.
- Directory-wide leases backed by `CEPH_CAP_FILE_SHARED` and `lease_shared_gen`.

Important helpers:
- `__ceph_dentry_lease_touch()` keeps valid dentry leases in LRU-like order.
- `__ceph_dentry_dir_lease_touch()` tracks directory-wide lease use.
- `dentry_lease_is_valid()` validates and optionally renews MDS leases.
- `dir_lease_is_valid()` validates directory-wide leases and touches file mode wanted state.
- `ceph_trim_dentries()` scans lease lists to drop stale dentries under cap pressure.
- `ceph_invalidate_dentry_lease()` invalidates a dentry lease and clears primary-link state.

## Dentry Revalidation and Pruning

`ceph_d_revalidate()`:
- Delegates fscrypt name revalidation first.
- Trusts snapped dentries and snapdir dentries.
- Uses valid per-dentry or directory-wide leases when available.
- Falls back to MDS lookup outside RCU-walk mode.
- Updates lease hit/miss metrics.
- Clears directory complete state when validation fails.

`ceph_d_delete()` permits VFS deletion of unused positive head dentries lacking valid lease coverage.

`ceph_d_prune()` clears complete or ordered directory cache state when the VFS prunes relevant dentries.

## Directory Stat Read

`ceph_read_dir()` implements the nonstandard `read()` on directories only when mounted with `DIRSTAT`. It formats local recursive and direct directory counts/bytes/ctime into a small text buffer.

## Important Dependencies

- `mds_client.h`: MDS request creation, request execution, request flags, path building, release counts, and session state.
- `crypto.h`: encrypted dentries, lookup/readdir preparation, encrypted symlink targets, encrypted request names.
- `super.h`: Ceph inode/dentry structures, caps, quotas, mount options, snapdir helpers.
- `ceph_frag.c`: fragment comparison used in readdir position ordering.
- `file.c`: `ceph_open()`, `ceph_release()`, `ceph_atomic_open()`, `ceph_fsync()`, locking/ioctl hooks.
- Linux VFS dentry, inode, namei, fscrypt, and directory iteration APIs.

## Edge Cases and Risks

- Readdir correctness depends on preserving `last_name`, fragment, hash-order, and offset semantics across MDS replies and seeks.
- Dcache readdir is only valid while directory shared-cap generation and ordered cache state remain intact.
- Unlocking an encrypted directory invalidates complete directory state because previously raw nokey names may become decryptable.
- Async unlink deliberately mutates local dcache/link state before server completion and must mark mapping errors if the server later fails the operation.
- Dentry lease trimming uses trylocks and RCU/list handoff to avoid blocking heavily while still dropping stale dentries.
- `ceph_d_prune()` defensively disables ordered dcache readdir if dentries disappear without an MDS revocation.
