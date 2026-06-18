# File Research: sources/os/linux/linux/fs/ntfs3/inode.c

## Role

Maps NTFS MFT records to Linux inodes and address-space behavior. It parses file records, sets VFS inode operations, implements iomap-backed reads/writes/writeback, handles resident and nonresident data, creates new MFT records, handles hardlink/unlink eviction helpers, and translates NTFS reparse-point symlinks/junctions.

## MFT Read and Inode Setup

- `ntfs_read_mft()` initializes `ntfs_inode`, reads the MFT record, validates sequence/in-use/base-record state, enumerates attributes, and derives Linux inode mode, size, timestamps, flags, operations, runlists, and link count.
- Handles key attributes:
  - `$STANDARD_INFORMATION`: timestamps, file attributes, security id.
  - `$ATTRIBUTE_LIST`: loads external attribute list and restarts enumeration.
  - `$FILE_NAME`: counts names and hardlink-visible names; optionally matches requested name.
  - `$DATA`: resident/nonresident size, valid size, compression/sparse/encryption flags, data runlist.
  - `$INDEX_ROOT`, `$INDEX_ALLOCATION`, `$BITMAP`: directory index setup.
  - `$REPARSE_POINT`: symlink/compression/dedup reparse parsing.
  - `$EA_INFO`: WSL permission/xattr state.
- Chooses `ntfs_dir_inode_operations`, `ntfs_link_inode_operations`, `ntfs_file_inode_operations`, or `ntfs_special_inode_operations`.
- Applies `sys_immutable` mount behavior for NTFS system files and sets `S_NOSEC` when there is no xattr/security state.
- `ntfs_iget5()` wraps `iget5_locked()`, reads new inodes, verifies sequence reuse, and marks the volume dirty on read failures.

## Address-Space and Iomap

- `ntfs_bmap()` supports FIBMAP/iomap bmap, forcing delayed-allocation blocks to be allocated before mapping.
- `ntfs_iomap_begin()` maps offsets to `IOMAP_INLINE`, `IOMAP_MAPPED`, `IOMAP_HOLE`, `IOMAP_UNWRITTEN`, or `IOMAP_DELALLOC`, using `attr_data_get_block()` and enforcing maximum file sizes.
- `ntfs_iomap_end()` writes back resident inline data and advances `ni->i_valid` after writes or zeroing.
- `ntfs_iomap_put_folio()` zeroes folio tail past valid data.
- `ntfs_iomap_read_end_io()` zero-fills folio ranges beyond NTFS valid data before completing iomap reads.
- `ntfs_read_folio()` handles bad inodes, reads past valid size as zero, dispatches compressed reads to `ni_read_folio_cmpr()`, and otherwise uses iomap.
- `ntfs_readahead()` skips resident and compressed files; otherwise uses iomap readahead.
- `ntfs_writeback_range()` allocates delayed blocks if needed and submits mapped writeback through iomap.
- `ntfs_writepages()` has a resident-data path via `attr_data_write_resident()` and a nonresident iomap writeback path.
- `ntfs_set_size()` changes file size through `attr_set_size()` under inode and runlist locks.

## Inode Write and Utility APIs

- `ntfs3_write_inode()` and `ntfs_sync_inode()` delegate to `_ni_write_inode()`.
- `inode_read_data()` reads metadata-file contents page by page, used for files such as `$AttrDef` and `$UpCase`.
- `ntfs_evict_inode()` truncates page cache, clears VFS inode state, and frees NTFS inode internals.

## Inode Creation

`ntfs_create_inode()` is the shared create path for create, mknod, symlink, mkdir, and atomic open:

- locks parent directory when needed;
- chooses NTFS file attributes from mode, parent attributes, sparse/compressed mount behavior, hidden dotfile option, and readonly mode;
- allocates a free MFT record and formats a new record;
- inserts standard information, filename, optional security descriptor, data/index/reparse attributes, and end marker;
- obtains/inserts security id through `$Secure` for NTFS 3.x volumes;
- creates `$I30` root for directories;
- creates NTFS symlink reparse data for symlinks, resident or nonresident depending on size;
- inserts reparse index entry for symlinks;
- initializes ACL/WSL permissions and updates directory-entry duplicated EA size;
- inserts the new name into parent `$I30` and instantiates the dentry;
- has rollback paths for EA, reparse index, allocated clusters, MFT record, and link count.

## Link, Unlink, and Reparse Reading

- `ntfs_link_inode()` builds a new filename directory entry and delegates to `ni_add_name()`.
- `ntfs_unlink_inode()` rejects metadata files, checks directory emptiness, removes the name, updates link counts/timestamps, and attempts undo on removal failure.
- `ntfs_create_reparse_buffer()` creates Windows symlink reparse buffers, converts path text to UTF-16, changes `/` to `\`, and decorates absolute paths with `\??\`.
- `ntfs_readlink_hlp()` reads resident or nonresident reparse data, supports symlink, mount point/junction, OneDrive cloud placeholders, and user surrogate tags, converts UTF-16 to mounted NLS, changes `\` to `/`, and translates junction targets relative to the mount point.
- `ntfs_get_link()` allocates PAGE_SIZE link text and registers delayed free.

## Exported Operation Tables

Defines `ntfs_link_inode_operations`, `ntfs_aops`, `ntfs_aops_cmpr`, `ntfs_iomap_ops`, and `ntfs_iomap_folio_ops`.

## Dependencies

Uses NTFS attribute, runlist, directory-index, xattr/ACL, compression, reparse, NLS, iomap, buffer-head, page-cache, writeback, and VFS inode APIs.

## Research Notes

This is the main NTFS3 VFS bridge. It is where on-disk MFT semantics become Linux inode semantics, and where NTFS valid-size, resident attributes, delayed allocation, compressed files, WSL permissions, and Windows reparse points are reconciled with Linux page-cache and namespace behavior.
