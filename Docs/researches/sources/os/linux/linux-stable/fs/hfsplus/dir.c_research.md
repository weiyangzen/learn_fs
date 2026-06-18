# File Research: sources/os/linux/linux-stable/fs/hfsplus/dir.c

## Scope

Provides HFS+ directory VFS operations: lookup, readdir, hardlink creation, unlink, rmdir, symlink, mknod/create/mkdir, rename, and directory operation tables.

## APIs And Behavior

- `hfsplus_lookup()` searches the catalog, resolves HFS+ hardlink proxy records through the hidden directory, stores catalog CNID in `d_fsdata`, and instantiates the target inode.
- `hfsplus_readdir()` emits `.`/`..`, walks catalog entries under a directory CNID, skips the hidden directory, converts Unicode names to mount charset, and emits file types from serialized modes.
- `hfsplus_link()` implements HFS+ hardlinks by moving the original file to the hidden directory if needed, creating catalog proxy records with new CNIDs, incrementing link count, and writing affected catalog records.
- `hfsplus_unlink()` handles open unlinked files by renaming them to hidden `temp*` records, deletes proxy and backing hidden records when link counts reach zero, and updates counts/dirty state.
- `hfsplus_rmdir()` enforces empty directories and deletes catalog records.
- `hfsplus_symlink()` writes the symlink body, creates catalog/security metadata, and instantiates the dentry.
- `hfsplus_mknod()` creates regular, directory, and special-file inodes, creates catalog records, initializes security xattrs, and writes catalog records.
- `hfsplus_rename()` supports only `RENAME_NOREPLACE`, removes existing destination entries, renames catalog records, transfers `d_fsdata`, and writes old/new dir and inode records.

## State And Dependencies

The file serializes namespace-changing operations with `vh_mutex`. It depends on catalog helpers, inode creation/deletion/writeback, hidden directory state, xattr security initialization, Unicode conversion, hardlink IDs, and open directory iterator tracking.

## Risks And Invariants

`d_fsdata` is semantically important because it stores the catalog CNID for proxy hardlink entries, which can differ from inode `i_ino`. Open-unlink handling relies on hidden temporary records and `S_DEAD`. Several operations write multiple catalog records after structural B-tree changes, so partial failure can leave work for fsck.
