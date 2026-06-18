# File Research: sources/os/linux/linux/fs/hfsplus/dir.c

Purpose: Provides HFS+ directory VFS operations, including lookup, readdir, hardlinks, unlink/rmdir, symlink, mknod/create/mkdir, rename, and operation tables.

Key functions:
- `hfsplus_lookup()` finds a catalog record, follows HFS+ hardlink indirection through the hidden directory when needed, sets `d_fsdata` to the catalog CNID, and returns the inode.
- `hfsplus_readdir()` emits synthetic `.`/`..`, walks catalog records, converts Unicode names to userspace charset, hides the hidden directory, and records iterator state.
- `hfsplus_link()` creates HFS+ hardlinks by moving the original file into the hidden directory when needed and creating link catalog records.
- `hfsplus_unlink()` removes catalog records, handles open unlinked files by moving to hidden temp names, manages hardlink counts, and deletes hidden backing records when possible.
- `hfsplus_rmdir()` removes empty directories.
- `hfsplus_symlink()` creates symlink inodes, writes symlink contents, creates catalog record, and initializes security xattrs.
- `hfsplus_mknod()` handles regular/special/dir creation with catalog and security initialization.
- `hfsplus_rename()` supports `RENAME_NOREPLACE`, deletes existing destination, renames catalog entries, and writes affected inodes.

Dependencies and integration:
- Uses catalog operations, security/xattr initialization, inode creation/deletion, and `vh_mutex` for volume-header/count-sensitive mutations.
- Exposes `hfsplus_dir_inode_operations` and `hfsplus_dir_operations`.

Risk notes:
- Hardlink behavior is complex and depends on hidden directory state, `d_fsdata`, link IDs, and open-count handling.
- Directory iteration allocates a charset-sized buffer and validates record sizes before emission.
