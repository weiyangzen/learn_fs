# File Research: sources/os/linux/linux-stable/fs/ntfs/namei.c

`namei.c` implements NTFS VFS directory inode operations: lookup, create, unlink, mkdir, rmdir, rename, symlink, mknod, hard link, and NFS export lookup helpers.

Key responsibilities:
- Validates NTFS/Windows names through `ntfs_check_bad_char()` and `ntfs_check_bad_windows_name()`, including reserved characters, trailing spaces/dots, and reserved DOS device names when configured.
- `ntfs_lookup()` converts dentries to Unicode, searches directory indexes with NTFS case semantics, handles exact WIN32/POSIX matches, case-insensitive aliases, and DOS short-name aliases via `d_add_ci()`.
- `ntfs_sd_add_everyone()` creates a simple self-relative security descriptor with administrator owner/group and an “everyone full access” ACE.
- `__ntfs_create()` is the common creation engine for regular files, directories, symlinks, and special files. It allocates an MFT record, initializes inode state, adds standard/security/data/index/reparse/EA/file-name attributes, inserts the directory index entry, and handles rollback.
- `ntfs_create()`, `ntfs_mkdir()`, `ntfs_symlink()`, and `ntfs_mknod()` convert names, mark the volume dirty if needed, call `__ntfs_create()`, and instantiate the VFS dentry.
- `ntfs_delete()` removes a filename from a directory index and from the target inode, handles DOS/WIN32 pair removal, decrements link count, checks directory emptiness, and triggers reparse/object-id index cleanup when the final link is removed.
- `ntfs_unlink()` and `ntfs_rmdir()` wrap `ntfs_delete()` and update timestamps/link state.
- `__ntfs_link()` creates a new `FILE_NAME` attribute and directory index entry, increments NTFS/VFS link counts for non-directories, and rolls back index insertion if attribute insertion fails.
- `ntfs_rename()` rejects exchange/whiteout, optionally deletes the target, links the source under the new name, deletes the old name, and rolls back the new link on delete failure where possible.
- `ntfs_get_parent()`, `ntfs_fh_to_dentry()`, and `ntfs_fh_to_parent()` provide NFS export support through parent lookup and generation validation.

Important data/control flow:
- File creation first allocates and maps an MFT record, then adds attributes in NTFS metadata order: standard information, security descriptor, directory index root or data attribute, reparse data for WSL symlinks/special files, WSL EA metadata, and file name.
- Symlinks and Unix special files are represented with WSL-compatible reparse tags and EA metadata.
- Directory index mutations and inode MFT mutations are paired; rollback paths try to remove partial attributes, reparse index entries, extent records, and the base MFT record.

Locking and safety notes:
- Directory and target MFT records use nested `mrec_lock` subclasses to preserve ordering.
- Create marks new inodes `I_NEW | I_CREATING` before hashing so writeback/iget paths can avoid unsafe access.
- Delete sets `NInoBeingDeleted()` on final unlink and clears nlink on cached attribute inodes.
- Volume dirty flag is set before mutating namespace metadata.

Exports:
- `ntfs_dir_inode_ops` installs lookup/create/unlink/mkdir/rmdir/rename/ACL/xattr/setattr/getattr/symlink/mknod/link operations.
- `ntfs_export_ops` installs NFS export callbacks.
