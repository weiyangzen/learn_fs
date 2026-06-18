# File Research: sources/os/linux/linux-stable/fs/ocfs2/namei.c

Purpose: implements OCFS2 namespace-changing VFS inode operations: lookup, create, mknod, mkdir, link, unlink/rmdir, rename, symlink creation, dentry-lock attachment, and the orphan-directory workflows used for normal unlink, rename-overwrite, direct-I/O append recovery, and creating orphan-staged inodes.

Read coverage: complete file read, 2,945 lines.

Key responsibilities:
- Provides `ocfs2_dir_iops`, wiring OCFS2 directory inodes to VFS create/lookup/link/unlink/rmdir/symlink/mkdir/mknod/rename plus attribute, ACL, xattr, fiemap, and fileattr handlers.
- Creates new dinodes with `ocfs2_mknod_locked()` / `__ocfs2_mknod_locked()`, populating on-disk fields, extent-list or inline-data layout, generation, suballocator location, ownership, timestamps, link count, device id, cluster lock resources, and fsync transaction tracking.
- Performs VFS lookups under parent inode cluster locks, resolves names to block numbers, loads inodes with `ocfs2_iget()`, clears stale maybe-orphan state, and attaches OCFS2 dentry lock state or negative-dentry generation state.
- Implements hard link creation with ordered double-directory locking, source-name revalidation, destination-space preparation, inode link-count journaling, directory insertion, and dentry-lock attach.
- Implements unlink/rmdir by locking parent and child, verifying on-disk directory entry identity, forcing remote dentry invalidation, optionally preparing an orphan-dir entry when the removed inode becomes unlinkable, deleting the parent entry, adjusting link counts and times, and adding normal orphans.
- Implements rename with cluster-wide rename locking for cross-directory directory moves, ancestor checks to avoid directory cycles, ordered parent and child locking, target race checks, target orphaning when overwritten, `..` updates, old-entry deletion, link-count/time updates, and dentry-lock move notification.
- Implements fast and allocated symlink creation, including security xattr setup, quota accounting, cluster reservation for slow symlinks, symlink-data block journaling, and inline symlink storage in the dinode.
- Implements orphan helpers for normal unlink orphans and DIO append orphans, including deterministic orphan names based on inode block numbers and the `dio-` prefix.

Important entry points:
- VFS operations: `ocfs2_lookup()`, `ocfs2_mknod()`, `ocfs2_mkdir()`, `ocfs2_create()`, `ocfs2_link()`, `ocfs2_unlink()`, `ocfs2_rename()`, `ocfs2_symlink()`.
- Creation internals: `ocfs2_get_init_inode()`, `ocfs2_mknod_locked()`, `__ocfs2_mknod_locked()`, `ocfs2_create_symlink_data()`.
- Lock ordering helpers: `ocfs2_double_lock()`, `ocfs2_double_unlock()`, `ocfs2_check_if_ancestor()`, `ocfs2_remote_dentry_delete()`.
- Orphan APIs exported through `namei.h`: `ocfs2_orphan_del()`, `ocfs2_create_inode_in_orphan()`, `ocfs2_add_inode_to_orphan()`, `ocfs2_del_inode_from_orphan()`, `ocfs2_mv_orphaned_inode_to_new()`.

Concurrency and ordering:
- Directory mutations take OCFS2 inode cluster locks and VFS inode mutexes in explicit parent/child/orphan-dir orders; `ocfs2_double_lock()` orders by ancestry and block number to avoid cross-node deadlocks.
- Cross-directory directory renames use the filesystem rename lock to serialize hierarchy moves across cluster nodes.
- Dentry cluster locks are attached before directory entry exposure so remote unlink/downconvert notifications cannot leave stale dentries behind.
- `ocfs2_remote_dentry_delete()` briefly takes an exclusive dentry lock to force other nodes to drop cached aliases before unlink or rename modifies names.
- Orphan-dir helpers return orphan directory inodes locked when callers need to combine orphan entry changes with an outer transaction.
- Signals are blocked after transactions begin in create/link/symlink paths once restart is no longer safe.

Journaling, quota, and allocation:
- Namespace operations reserve inode, metadata, cluster, security xattr, ACL, and directory-insert resources before starting journal transactions.
- New directory creation accounts for inline-data support, indexed-directory metadata, parent link count, and new directory initialization through `ocfs2_fill_new_dir()`.
- Symlink creation distinguishes fast symlinks stored in `ocfs2_dinode.id2.i_symlink` from slow symlinks backed by allocated clusters and `ocfs2_aops`.
- Quota initialization and `dquot_alloc_inode()` / `dquot_free_inode()` / `dquot_alloc_space_nodirty()` cleanup are paired with inode and cluster allocation.

Dependencies:
- Uses OCFS2 directory lookup/insert/delete/update helpers, dcache/dentry locks, DLM glue, inode loading/population, journaling, suballocators, local/global quota hooks, xattr/security/ACL initialization, extent maps, file truncation, and system-file lookup.
- Relies on VFS inode/dentry operations, idmapped mount prototypes, quota core, buffer heads, JBD2 handles, and Linux timestamp/link-count helpers.

Risk and edge cases:
- Many operations revalidate on-disk directory entries after VFS lookup because another cluster node can remove or replace names while local code waits for locks.
- Failed create/symlink after dentry-lock attachment must explicitly tear down `d_fsdata`; otherwise dentry lock resources leak.
- Unlink and rename-overwrite must add last-link files to the orphan dir before commit so crash recovery can finish deletion.
- Rename reports filesystem errors if the new entry is added but old-entry deletion then fails outside an aborted journal.
- Directory ancestry checks are bounded by `MAX_LOOKUP_TIMES`; hitting the bound logs a notice and treats the move as not proven ancestral.
- DIO orphan helpers must recover an existing `OCFS2_DIO_ORPHANED_FL` state before adding a new DIO orphan entry.
