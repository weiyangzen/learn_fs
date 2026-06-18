# File Research: sources/os/linux/linux-stable/fs/ntfs/inode.h

## Summary
Defines the Linux NTFS in-memory inode model and the inode/attribute lifecycle API shared by the NTFS driver. It bridges VFS `struct inode` objects, NTFS MFT records, fake attribute inodes, extent records, runlists, attribute lists, index metadata, compression metadata, and delayed allocation state.

## Main Contents
- `enum ntfs_inode_mutex_lock_class` lockdep classes for parent/child inode, extension, and EA mutex nesting.
- `struct ntfs_inode`, the main per-NTFS-inode state container.
- `NI_*` state bits plus generated `NIno*`, `NInoSet*`, `NInoClear*`, `NInoTestSet*`, and `NInoTestClear*` helpers.
- `struct big_ntfs_inode`, `NTFS_I()`, and `VFS_I()` for embedding NTFS inode state inside VFS inodes.
- `struct ntfs_attr`, the key used by `iget` paths for named/fake attribute inodes.

## Key Interfaces
Declares inode lookup and allocation helpers (`ntfs_iget()`, `ntfs_attr_iget()`, `ntfs_index_iget()`, `ntfs_alloc_big_inode()`), eviction/drop/free paths, mount-time inode loading, truncate/setattr/getattr operations, MFT writeback, extent attachment/destruction, attribute pread/pwrite, initialized-size extension, operation-table setup, and locked-folio acquisition.

## Important Details
`struct ntfs_inode` is polymorphic. For real inodes it describes the base or extent MFT record; for fake attribute inodes `NI_Attr` is set and `type/name/name_len` describe the represented attribute while `ext.base_ntfs_ino` points back to the owning base inode. `nr_extents` distinguishes base records with loaded extents from extent/fake inodes.

The inode tracks both on-disk values (`mft_no`, sequence number, file flags, sizes, timestamps, attribute-list data, MFT record pointer) and runtime state (`runlist`, locks, folio offset, MFT LCN mapping, delayed cluster count, symlink target).

## Risks
Many consumers depend on the state-bit protocol and the fake-inode/base-inode distinction. Lock ordering is explicit but fragile around `mrec_lock`, `size_lock`, `runlist.lock`, and `extent_lock`. The comment notes dirty MFT records are still tied to inode lifetime rather than an independent dirty-record list.
