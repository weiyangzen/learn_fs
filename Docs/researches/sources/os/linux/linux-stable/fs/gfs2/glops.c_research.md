# File Research: sources/os/linux/linux-stable/fs/gfs2/glops.c

## Scope

This file defines glock operation callbacks for metadata, inode, resource-group, freeze, iopen, flock, nondisk, quota, and journal glocks. These callbacks plug lock-type-specific sync, invalidate, instantiate, held, dump, and remote-callback behavior into the generic glock state machine.

## Public And Internal APIs Covered

- Exported workqueue: `gfs2_freeze_wq`.
- AIL helpers: `gfs2_ail_flush()` and internal `__gfs2_ail_flush()` / `gfs2_ail_empty_gl()`.
- Metadata sync: `gfs2_inode_metasync()`.
- Object lookup helper: `gfs2_glock2rgrp()`.
- Operation tables: `gfs2_meta_glops`, `gfs2_inode_glops`, `gfs2_rgrp_glops`, `gfs2_freeze_glops`, `gfs2_iopen_glops`, `gfs2_flock_glops`, `gfs2_nondisk_glops`, `gfs2_quota_glops`, `gfs2_journal_glops`, and `gfs2_glops_list[]`.

## Control Flow And Behavior

- AIL flushing scans a glock’s AIL list, verifies buffers are not dirty/locked/pinned outside fsync mode, converts buffers to revokes, and flushes the log. Unexpected dirty/locked/pinned AIL buffers withdraw the filesystem.
- Resource-group sync flushes the log for the rgrp glock, writes/waits metadata pages covering the rgrp blocks, empties the glock AIL, and frees bitmap clones. Invalidation releases rgrp buffers and truncates metadata pages over the rgrp range.
- Inode sync first handles regular-file concerns: unmaps shared mappings marked by mmap write faults and waits for direct I/O. If dirty, it flushes the log, writes metadata and regular data mappings, waits, metasyncs, empties AIL, then clears dirty state.
- Inode invalidation asserts no AIL buffers remain, truncates metadata mapping when metadata invalidation is requested, marks instantiate-needed, drops ACL/security/dir hash caches, marks the rindex stale when invalidating it, and truncates regular-file page cache.
- Dinode refresh parses on-disk dinode fields into the in-core inode, validates inode number, type, height, directory depth, exhash consistency, stuffed size limits, and sets VFS inode flags/address-space ops.
- Inode instantiate reads the dinode if a `gl_object` inode exists and updates the iopen glock’s formal inode number.
- Inode held waits for direct I/O except deferred holders and resumes interrupted truncation when taking exclusive lock on an inode flagged `GFS2_DIF_TRUNC_IN_PROG`.
- Freeze callback reacts to remote freeze demotion requests by trying to pin the superblock active and queueing freeze work. Freeze xmote bottom-half invalidates the journal glock and reloads log pointers from the journal head.
- Iopen callback reacts to remote unlock requests by scheduling local inode eviction when the iopen glock is shared and has an inode object.

## State And Data Structures

- Uses `gl_object` as either `gfs2_inode` or `gfs2_rgrpd`, guarded by `gl_lockref.lock`.
- `GIF_GLOP_PENDING` serializes inode glop activity with waiters.
- AIL state is stored in `gl_ail_list`, `gl_ail_count`, `sd_ail_lock`, `sd_log_lock`, and revoke lists.
- Inode parsing fills `i_no_formal_ino`, `i_generation`, `i_diskflags`, `i_eattr`, `i_goal`, `i_height`, `i_depth`, `i_entries`, VFS timestamps, uid/gid, nlink, size, blocks, mode, and rdev.

## Dependencies

- Relies on glock core for state transitions, transactions/logging for AIL and flushes, rgrp code for rgrp instantiation/dump/free clones, metadata I/O for dinode buffers, directory/xattr/security cache helpers, recovery for journal head discovery, and VFS address-space writeback/invalidation.

## Risks And Invariants

- Demotion must not complete before dirty metadata/data and AIL entries are stable or revoked.
- Invalidation assumes AIL is empty; assertions withdraw on inconsistency.
- Dinode parsing is a trust boundary from disk to memory; all structural checks protect later metadata traversal.
- Freeze handling must avoid racing unmount; it uses `s_umount` trylock plus active superblock reference.
- Iopen callback must avoid scheduling delete work during filesystem kill.
