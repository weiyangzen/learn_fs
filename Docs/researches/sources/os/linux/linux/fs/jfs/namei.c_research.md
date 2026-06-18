# File Research: sources/os/linux/linux/fs/jfs/namei.c

JFS VFS namespace operation implementation for create, lookup, link, unlink, directory creation/removal, rename, symlink, mknod, and export lookup.

Key responsibilities:
- Implements `jfs_create()`, allocating a new inode, initializing ACL/security xattrs, initializing an xtree root, inserting the parent dtree entry, and committing both inodes.
- Implements `jfs_mkdir()` and `jfs_rmdir()`, including dtree initialization, parent link-count updates, empty-directory checks, and EA/ACL cleanup.
- Implements `jfs_unlink()`, deleting the directory entry, decrementing link count, and using zero-link truncation for the final unlink.
- Implements `commitZeroLink()` and `jfs_free_zero_link()` to split persistent-map freeing from later working-map cleanup for open-but-unlinked files.
- Implements hard link creation in `jfs_link()`, including read-only checks and link-count updates.
- Implements `jfs_symlink()`, storing short symlink targets inline and longer targets in a single xtree-backed extent.
- Implements `jfs_rename()`, including overwrite semantics, directory parent updates, link-count handling, victim cleanup, and iterative pmap truncation.
- Implements `jfs_mknod()` for device/special inode creation.
- Implements `jfs_lookup()` and NFS export helpers `jfs_fh_to_dentry()`, `jfs_fh_to_parent()`, and `jfs_get_parent()`.
- Defines directory inode/file operations and optional case-insensitive dentry operations.

Important interactions:
- Uses JFS dtree operations `dtSearch()`, `dtInsert()`, `dtDelete()`, `dtModify()`, `dtEmpty()`, and `dtInitRoot()`.
- Uses inode allocation/loading helpers `ialloc()` and `jfs_iget()`.
- Uses transaction manager helpers `txBegin()`, `txCommit()`, `txAbort()`, and `txEnd()`.
- Coordinates with xtree truncation through `xtInitRoot()`, `xtInsert()`, `xtTruncate()`, and `xtTruncate_pmap()`.
- Uses quota initialization, ACL initialization, security xattr initialization, and EA/ACL map freeing.
- Uses nested `commit_mutex` ordering for parent, child, second parent, and rename victim inodes.

Invariants and risks:
- Directory dtree pages may be pinned by search, so inode allocation and transaction begin are deliberately done before `dtSearch()` in create paths.
- Failed creates must free uncommitted EA working-map allocations, clear links, and discard the new inode.
- Unlink and rename may require synchronous commits when `xtTruncate_pmap()` only partially frees a large fragmented file.
- `COMMIT_Stale` directory truncation is opportunistic and may need repeated `jfs_truncate_nolock()` calls.
- Rename handles only default and `RENAME_NOREPLACE`; other flags return `-EINVAL`.
- Case-insensitive dentry revalidation intentionally drops negative dentries for create/rename-target intents to preserve user-specified case.
