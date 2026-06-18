# File Research: sources/os/linux/linux-stable/fs/ufs/namei.c

## Summary
Implements UFS directory inode operations for VFS name lookup and namespace mutation: create, lookup, link, unlink, symlink, mkdir, rmdir, mknod, and rename.

## Key APIs
- `ufs_lookup()`
- `ufs_create()`
- `ufs_mknod()`
- `ufs_symlink()`
- `ufs_link()`
- `ufs_mkdir()`
- `ufs_unlink()`
- `ufs_rmdir()`
- `ufs_rename()`
- `ufs_dir_inode_operations`

## Important Behavior
Creation allocates a UFS inode with `ufs_new_inode()`, assigns file or special inode operations, marks it dirty, and inserts a directory entry through `ufs_add_link()`. `ufs_add_nondir()` centralizes successful dentry instantiation and failure cleanup for non-directories.

Lookup rejects names longer than `UFS_MAXNAMLEN`, resolves directory entries with `ufs_inode_by_name()`, and uses `d_splice_alias()` for VFS alias handling.

Symlink creation supports fast symlinks stored in `ufs_inode_info.i_u1.i_symlink` when the link fits `s_maxsymlinklen`; longer symlinks use page-cache symlink storage and `ufs_aops`.

Directory creation increments the parent link count before allocation, initializes `.` and `..` with `ufs_make_empty()`, then inserts the new entry. Failure paths carefully undo both new-directory and parent link counts.

Unlink and rmdir locate entries with `ufs_find_entry()`, remove them using `ufs_delete_entry()`, update ctime/link counts, and release mapped folios. `ufs_rmdir()` only proceeds when `ufs_empty_dir()` succeeds.

Rename handles only default rename and `RENAME_NOREPLACE`; other flags return `-EINVAL`. Directory renames update the child `..` entry through `ufs_dotdot()`/`ufs_set_link()`, adjust parent link counts, and replace or add the target entry before deleting the old entry.

## Dependencies
Relies on UFS directory helpers from `dir.c`, allocation from `ialloc.c`, inode loading/writing from `inode.c`, page-cache folio mapping, VFS dentry/inode helpers, and metadata helpers from `ufs.h`/`util.h`.

## Risks
Rename correctness depends on preserving ordering across target replacement, source deletion, and `..` updates. Link-count rollback paths are important for failed create/mkdir/symlink operations. Fast symlink bounds depend on mount-time `s_maxsymlinklen` validation.
