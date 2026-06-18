# File Research: sources/os/linux/linux/fs/ntfs/inode.h

This header defines the NTFS driver's in-memory inode model and its primary inode-facing APIs. It extends the VFS inode through `struct big_ntfs_inode`, where `struct ntfs_inode` is embedded before `struct inode`, and provides `NTFS_I()` / `VFS_I()` container conversion helpers.

Key data model:
- `struct ntfs_inode` stores NTFS-specific state: MFT number/sequence, volume pointer, attribute identity, runlist, size triplet (`data_size`, `initialized_size`, `allocated_size`), MFT record cache fields, attribute-list state, index/compression subtype metadata, extent tracking, delayed allocation cluster count, and symlink target.
- `enum ntfs_inode_mutex_lock_class` provides lockdep classes for parent/child/extent/EA locking patterns.
- The `state` bitset is exposed via generated `NIno*`, `NInoSet*`, `NInoClear*`, and selected test-and-set/test-and-clear helpers. State flags cover dirty MFT records, attribute lists, fake attribute inodes, MST protection, non-resident/index/compressed/encrypted/sparse state, fully mapped runlists, filename dirty state, deletion/creation, EA presence, and dirty runlists.
- `struct ntfs_attr` is a compact lookup key for attribute inodes, carrying MFT number, attribute name/type, name length, and state.

Concurrency and lifecycle:
- `size_lock` serializes inode size fields.
- `mrec_lock` protects the loaded MFT record for the inode.
- `extent_lock` protects extent inode attachment state.
- Runlist locking is delegated to `struct runlist` internals.

Exported interface:
- Inode lookup/allocation: `ntfs_iget`, `ntfs_attr_iget`, `ntfs_index_iget`, `ntfs_alloc_big_inode`, `ntfs_free_big_inode`, `ntfs_drop_big_inode`, `ntfs_evict_big_inode`.
- Initialization and mount-time load: `__ntfs_init_inode`, `ntfs_init_big_inode`, `ntfs_new_extent_inode`, `ntfs_clear_extent_inode`, `ntfs_read_inode_mount`.
- VFS operations: `ntfs_setattr`, `ntfs_getattr`, `ntfs_truncate_vfs`, `ntfs_set_vfs_operations`.
- MFT/extent/attribute maintenance: `ntfs_get_block_mft_record`, `__ntfs_write_inode`, `ntfs_inode_attach_all_extents`, `ntfs_inode_add_attrlist`, `ntfs_destroy_ext_inode`, `ntfs_inode_free_space`, `ntfs_inode_close`, `ntfs_inode_sync_filename`.
- Attribute I/O and initialization extension: `ntfs_inode_attr_pread`, `ntfs_inode_attr_pwrite`, `ntfs_extend_initialized_size`.
- Folio helper: `ntfs_get_locked_folio`.

Role in subsystem:
This is the central contract between NTFS metadata code, VFS inode operations, runlist mapping, iomap I/O, and MFT persistence. Most implementation files in this group consume `NTFS_I()` and the state helpers defined here.
