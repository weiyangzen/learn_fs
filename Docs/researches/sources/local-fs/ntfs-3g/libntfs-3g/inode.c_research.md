# File Research: sources/local-fs/ntfs-3g/libntfs-3g/inode.c

## Purpose
Implements NTFS inode lifecycle, dirty tracking, MFT record open/close, extent inode attachment, inode writeback, attribute-list creation, MFT-record space reclamation, timestamp helpers, and `$BadClus:$Bad` detection.

## Main Interfaces
- `ntfs_inode_base()` returns the base inode for extent inodes.
- `ntfs_inode_mark_dirty()` marks an inode and its base inode dirty.
- `ntfs_inode_allocate()` allocates an initialized in-memory inode shell.
- `ntfs_inode_open()` opens an MFT record, optionally through the nidata cache.
- `ntfs_inode_close()` syncs and either caches or releases an inode.
- `ntfs_inode_real_close()` performs actual close/release and closes extent inodes.
- `ntfs_extent_inode_open()` opens and attaches an extent MFT record to a base inode.
- `ntfs_inode_attach_all_extents()` walks an attribute list and attaches all referenced extents.
- `ntfs_inode_sync()` writes standard information, filename index state, attrlist data, and MFT records.
- `ntfs_inode_close_in_dir()` syncs while reusing an already-open parent directory inode.
- `ntfs_inode_add_attrlist()` creates and populates `$ATTRIBUTE_LIST`.
- `ntfs_inode_free_space()` moves eligible attributes out of the base record to free MFT-record space.
- `ntfs_inode_update_times()`, `ntfs_inode_get_times()`, and `ntfs_inode_set_times()` maintain NTFS timestamps.
- `ntfs_inode_badclus_bad()` identifies `$BadClus:$Bad`.

## Control Flow and State
Opening reads and validates the MFT record through `ntfs_file_record_read()`, extracts `$STANDARD_INFORMATION`, loads optional `$ATTRIBUTE_LIST`, and derives unnamed `$DATA` size state. Closing first syncs dirty metadata, then closes attached extents or disconnects an extent from its base inode before release. Cache-enabled builds avoid full release for non-system reusable inode data.

Sync ordering is deliberate: standard information, filename index entries, attrlist attribute contents, current MFT record, then dirty extent records. Filename sync updates parent directory `$I30` index entries and propagates file size, attributes, timestamps, and reparse tags.

## Integration Points
Depends heavily on `attrib.c`, `attrlist.c`, `mft.c`, `index.c`, `dir.c`, `lcnalloc.c`, `cache.c`, `ntfstime.c`, and `xattrs.h`. It is central glue between on-disk MFT records and higher-level file/directory operations.

## Risks and Invariants
- Reopening an inode is explicitly warned against because stale cache entries can be reused.
- Extent inode handling must avoid duplicate attachments and stale sequence references.
- `$MFT` extent lookup has special anti-recursion checks because malformed MFT extent placement can become unreadable.
- Rollback in `ntfs_inode_add_attrlist()` attempts to restore moved attributes, but failed rollback is logged as possible corruption.
- Timestamp setters mark `TimesSet` to avoid close-time lower-precision overwrite.
