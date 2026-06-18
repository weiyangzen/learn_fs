# File Research: sources/os/linux/linux-stable/fs/ntfs3/inode.c

## Role

NTFS3 inode bridge between MFT records and Linux VFS/iomap. It reads and validates MFT records, derives VFS inode mode/operations from NTFS attributes, implements folio read/readahead/writeback through iomap, changes file size, creates and deletes inodes, manages hard links, and implements symlink/reparse readback.

## Key Functions

- `ntfs_read_mft()` parses one MFT record into a Linux inode.
  - Validates record sequence, in-use state, base-record status, and record size.
  - Handles `$STANDARD_INFORMATION`, `$ATTRIBUTE_LIST`, `$FILE_NAME`, `$DATA`, `$INDEX_ROOT`, `$INDEX_ALLOCATION`, `$BITMAP`, `$REPARSE_POINT`, and `$EA_INFO`.
  - Initializes directory indexes, data run trees, inode size/valid size, timestamps, mode, file operations, and address-space operations.
  - Handles special cases for `$MFT`, `$Bitmap`, `$Secure:$SDS`, `$BadClus`, `$Extend` children, compressed/sparse/encrypted flags, and reparse symlinks.
- `ntfs_iget5()` wraps `iget5_locked()`, reads fresh inodes, and rejects stale sequence numbers.
- `ntfs_bmap()` maps logical blocks via iomap, forcing delayed allocation materialization first when needed.
- `ntfs_iomap_read_end_io()` zeros bytes past NTFS valid-data length before completing folio reads.
- `ntfs_read_folio()` reads resident, normal, and compressed data paths.
- `ntfs_readahead()` enables iomap readahead for nonresident, noncompressed files.
- `ntfs_set_size()` grows/truncates the unnamed data attribute and updates `i_size`.
- `ntfs_iomap_begin()` maps NTFS extents into iomap states: inline, mapped, hole, unwritten, or delalloc.
- `ntfs_iomap_end()` writes back inline resident data and advances valid-data length after writes/zeroing.
- `ntfs_iomap_put_folio()` zeroes folio tails past `i_valid` during buffered write/zero operations.
- `ntfs_writeback_range()` maps writeback ranges, forcing delayed allocation blocks when necessary.
- `ntfs_resident_writepage()` writes resident data from folios into the MFT resident attribute.
- `ntfs_writepages()` dispatches resident writeback or iomap writepages.
- `ntfs3_write_inode()` and `ntfs_sync_inode()` flush MFT inode metadata.
- `inode_read_data()` reads file contents page-by-page for metadata files such as `$AttrDef` and `$UpCase`.
- `ntfs_create_reparse_buffer()` builds Windows symlink reparse data from a Linux path.
- `ntfs_create_inode()` creates files, directories, symlinks, and special nodes.
  - Allocates an MFT record.
  - Builds standard info, filename, optional security, data/root, and reparse attributes.
  - Inserts the directory index entry.
  - Initializes ACL/WSL permission metadata and handles rollback on failure.
- `ntfs_link_inode()` constructs a new filename entry and delegates link insertion.
- `ntfs_unlink_inode()` removes a name, checks directory emptiness, drops link count, and attempts undo on failure.
- `ntfs_evict_inode()` truncates cached pages and clears NTFS inode state.
- `ntfs_readlink_hlp()` reads and decodes reparse targets for symlinks, mount points, cloud placeholders, and user tags.
- `ntfs_translate_junction()` converts absolute Windows junction targets into Linux-relative paths.
- `ntfs_get_link()` supplies VFS symlink targets.

## VFS Exports

- `ntfs_link_inode_operations` for symlinks.
- `ntfs_aops` for normal address-space operations.
- `ntfs_aops_cmpr` for compressed-file read support.
- `ntfs_iomap_ops` and `ntfs_iomap_folio_ops` for iomap integration.

## Research Notes

This file is where NTFS metadata semantics become Linux inode behavior. The most important invariants are sequence-number freshness, valid-data-length zeroing, resident versus nonresident data handling, run-tree locking during size/mapping changes, and careful rollback during inode creation.
