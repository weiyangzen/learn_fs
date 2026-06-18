# File Research: sources/os/linux/linux-stable/fs/hfs/dir.c

## Scope

Provides classic HFS directory VFS operations: lookup, readdir, create, mkdir, unlink/rmdir, rename, directory release, and operation tables.

## APIs And Behavior

- `hfs_lookup()` searches the catalog by parent/name and instantiates an inode with `hfs_iget()`.
- `hfs_readdir()` emits synthetic `.` and `..`, resolves the folder thread for the parent ID, then walks catalog records under the current directory CNID, converting Mac names to Linux names.
- `hfs_create()` and `hfs_mkdir()` allocate a new inode, create catalog records, instantiate the dentry, and roll back inode state on catalog failure.
- `hfs_remove()` enforces directory emptiness, rejects operations if CNID counters are out of range, deletes catalog records, clears link count, and truncates/deletes the inode.
- `hfs_rename()` supports only `RENAME_NOREPLACE`, removes any existing destination, moves catalog records, and updates the moved inode's cached catalog key.

## State And Dependencies

Directory offsets use `inode->i_size` with two synthetic entries included. The file depends on catalog helpers, inode creation/deletion/truncation, dcache splice helpers, and per-inode open directory readdir tracking.

## Risks And Invariants

`hfs_readdir()` requires catalog records to stay grouped by parent CNID; walking past that boundary is treated as `-EIO`. HFS has no hardlinks, so unlink and rmdir both clear the target link count after the directory-specific emptiness check. Rename first deletes any target entry, so partial failures after target removal can be externally visible.
