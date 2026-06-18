# File Research: sources/os/linux/linux/fs/ocfs2/namei.c

Role: Implements OCFS2 VFS namespace operations for lookup, create, mkdir, mknod, link, unlink/rmdir, rename, symlink, and orphan-directory transitions. It installs `ocfs2_dir_iops`, making this file the directory inode operation table for OCFS2.

Key responsibilities:
- `ocfs2_lookup()` validates name length, locks the parent directory, maps name to block number, gets the inode, clears stale `OCFS2_INODE_MAYBE_ORPHANED`, uses `d_splice_alias()`, and attaches OCFS2 dentry locking or a generation marker for negative dentries.
- `ocfs2_get_init_inode()` creates a VFS inode, initializes ownership/mode, sets directory link count to 2, strips SGID as needed, and initializes quota state.
- `ocfs2_mknod()` is the common create path for regular files, directories, device nodes, and named pipes. It reserves inode/data/metadata allocation contexts, computes ACL/security xattr needs, starts a journal transaction, allocates quota, creates the dinode, initializes directory contents if needed, writes ACL/security xattrs, attaches the dentry lock, adds the directory entry, hashes the inode, and instantiates the dentry.
- `__ocfs2_mknod_locked()` formats a new `ocfs2_dinode`: generation, owner, mode, device number, link count, timestamps, signatures, validity flags, inline-data or extent-list initialization, inode population, lock resource creation, and fsync transaction tracking.
- `ocfs2_mknod_locked()` claims a new inode from suballocation and delegates formatting to `__ocfs2_mknod_locked()`.
- `ocfs2_mkdir()` and `ocfs2_create()` are thin wrappers over `ocfs2_mknod()` with `S_IFDIR` or `S_IFREG`.
- `ocfs2_link()` locks source and destination parent directories with `ocfs2_double_lock()`, verifies the old name still refers to the expected inode, locks the target inode, checks link limits, journals link-count and ctime updates, adds the new dirent, attaches dentry locking, and instantiates the hard link.
- `ocfs2_unlink()` covers unlink and rmdir. It locks parent and child, verifies the dirent still targets the expected inode, checks directory emptiness, forces remote dentry invalidation, prepares the orphan dir when the link count will reach zero, deletes the parent entry, updates link counts and parent timestamps, and adds the inode to the orphan dir when needed.
- `ocfs2_rename()` serializes cross-directory directory renames with the cluster rename lock, locks both parents in deadlock-safe order, locks old and possibly new child inodes, validates source and target races, updates or adds target entries, removes the old entry, updates `..` for moved directories, adjusts link counts, optionally orphans overwritten targets, and moves OCFS2 dentry lock state.
- `ocfs2_symlink()` creates fast inline symlinks when the target fits in `ocfs2_fast_symlink_chars()`, otherwise reserves a data cluster, adds extent-backed symlink data via `ocfs2_create_symlink_data()`, initializes xattrs/security, and installs symlink inode operations.
- `ocfs2_create_symlink_data()` writes the symlink target plus NUL into newly allocated data blocks under journal access.
- `ocfs2_check_if_ancestor()` walks `..` links with a capped lookup count to help order nested directory locks and prevent invalid directory renames.
- `ocfs2_double_lock()` orders two directory inode locks by ancestry and block number, using lockdep subclasses for rename vs parent locking.

Orphan handling:
- Orphan names are block numbers formatted as 16 hex characters; direct-IO append orphans add the `dio-` prefix from `namei.h`.
- `ocfs2_lookup_lock_orphan_dir()` gets and exclusively locks the current slot’s orphan directory.
- `ocfs2_prepare_orphan_dir()` and `__ocfs2_prepare_orphan_dir()` compute the orphan name and prepare an insertion slot.
- `ocfs2_orphan_add()` journals orphan-dir and inode changes, inserts the orphan dirent, sets `OCFS2_ORPHANED_FL` or `OCFS2_DIO_ORPHANED_FL`, records the slot, and adjusts orphan directory link count for directories.
- `ocfs2_orphan_del()` removes an orphan dirent and fixes orphan directory link count.
- `ocfs2_prep_new_orphaned_file()` reserves a new inode location before inode creation so the orphan dirent can be named by the future dinode block.
- `ocfs2_create_inode_in_orphan()` creates a new unlinked inode directly in the orphan directory and takes its open lock.
- `ocfs2_add_inode_to_orphan()` handles append-DIO orphaning, including recovery if an inode is already marked `OCFS2_DIO_ORPHANED_FL`.
- `ocfs2_del_inode_from_orphan()` removes an append-DIO orphan, clears DIO orphan flags, and optionally updates inode size.
- `ocfs2_mv_orphaned_inode_to_new()` moves a previously orphaned inode into a visible directory entry, clears orphan state, restores link count, attaches dentry locking, and instantiates the dentry.

Concurrency and integrity:
- Directory operations use OCFS2 inode cluster locks, dentry locks, the global rename lock, and careful lock ordering to handle multi-node races.
- Journal transactions wrap metadata mutations; rollback paths repair link counts, quota allocations, dentry lock state, and newly created inodes.
- Dentry operations are intentionally ordered so cluster lock release happens after dentry insertion/attachment, preventing stale negative or disconnected dentries after remote unlink/create races.
- Quota initialization/allocation/freeing is integrated into create, symlink, link/unlink, and orphan paths.
- Signal blocking is used once transactions become non-restartable.
