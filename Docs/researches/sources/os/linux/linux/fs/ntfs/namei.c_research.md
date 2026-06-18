# File Research: sources/os/linux/linux/fs/ntfs/namei.c

Implements NTFS directory inode operations, namespace lookup, create/delete/link/rename, symlink/mknod support, and NFS export helpers.

Lookup:
- `ntfs_lookup()` converts dentries to Unicode and calls `ntfs_lookup_inode_by_name()`.
- Handles exact WIN32/POSIX matches directly through `d_splice_alias()`.
- Handles case-insensitive WIN32 matches with `d_add_ci()`.
- Handles DOS short-name matches by loading the inode, locating the corresponding WIN32 `FILE_NAME` attribute, converting it to NLS, then returning the canonical dentry.
- Checks MFT reference sequence numbers to reject stale directory index entries.

Name validation:
- `ntfs_check_bad_char()` rejects NTFS/Windows-disallowed characters and control chars.
- `ntfs_check_bad_windows_name()` optionally rejects trailing space/dot and reserved DOS device names like `AUX`, `CON`, `NUL`, `PRN`, `COM1`-`COM9`, and `LPT1`-`LPT9`.

Create path:
- `__ntfs_create()` creates a VFS inode, initializes NTFS inode state, allocates an MFT record, sets `I_NEW | I_CREATING`, inserts into inode hash, and constructs core attributes.
- Adds `STANDARD_INFORMATION`, a permissive `SECURITY_DESCRIPTOR`, directory `INDEX_ROOT` or unnamed `DATA`, WSL EA metadata, and a POSIX `FILE_NAME`.
- For symlinks and special files, creates WSL-compatible reparse data via `ntfs_reparse_set_wsl_symlink()` or `ntfs_reparse_set_wsl_not_symlink()`.
- Adds the filename to the parent directory index and updates link count.
- Rollback removes created attributes, reparse index entries, extent records, and MFT record on failure.

Delete/unlink/rmdir:
- `ntfs_delete()` removes matching `FILE_NAME` attributes and directory index entries.
- Handles DOS/WIN32 paired names, case-sensitive first then case-insensitive fallback.
- Checks directory emptiness, with hard-link-aware handling for directories.
- When link count reaches zero, sets `NInoBeingDeleted()`, deletes reparse and object-id index entries, and clears attribute inode links.

Hard links and rename:
- `__ntfs_link()` adds a new POSIX `FILE_NAME` attribute and parent index entry, then increments MFT/VFS link counts.
- `ntfs_rename()` rejects exchange/whiteout, optionally deletes existing target, links old inode into the new directory, deletes the old name, and attempts rollback if old-name deletion fails.

VFS operations:
- `ntfs_dir_inode_ops` wires lookup, create, unlink, mkdir, rmdir, rename, ACL, xattr, setattr/getattr, symlink, mknod, and link.
- `ntfs_create()`, `ntfs_mkdir()`, `ntfs_symlink()`, and `ntfs_mknod()` all mark the volume dirty before metadata mutation.

Export support:
- `ntfs_get_parent()` reads the first valid resident `FILE_NAME` attribute to obtain parent MFT reference.
- `ntfs_export_ops` uses generic file-handle encoding/decoding with sequence generation checks.

Important dependencies:
- Attribute, index, EA, reparse, object-id, ACL, timestamp, MFT, and Unicode conversion helpers.
- Careful nested locking of child, old/new parent, and target mrec locks.
