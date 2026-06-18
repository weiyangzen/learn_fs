# File Research: sources/os/linux/linux-stable/fs/hfsplus/inode.c

## Role

Implements HFS+ inode handling and regular-file VFS operations. It connects Linux page-cache/block-mapping helpers to HFS+ extent mapping, manages file open/release semantics, serializes/deserializes HFS+ catalog file/folder records, handles inode attributes, and participates in metadata sync.

## Address-Space and Dentry Operations

- `hfsplus_read_folio()` uses `block_read_full_folio()` with `hfsplus_get_block`.
- `hfsplus_write_begin()` uses `cont_write_begin()` and tracks `HFSPLUS_I(mapping->host)->phys_size`; on failure it calls `hfsplus_write_failed()`.
- `hfsplus_write_failed()` truncates page cache and HFS+ file allocation back to inode size if a failed extending write allocated beyond EOF.
- `hfsplus_bmap()` delegates to `generic_block_bmap()`.
- `hfsplus_direct_IO()` uses `blockdev_direct_IO()` and trims newly instantiated blocks after failed extending writes.
- `hfsplus_writepages()` delegates to `mpage_writepages()`.
- `hfsplus_btree_aops` adds `release_folio = hfsplus_release_folio` for metadata B-tree inodes.
- `hfsplus_aops` is the regular file/symlink mapping ops table.
- `hfsplus_dentry_operations` wires HFS+ Unicode-aware dentry hash and compare functions.

## B-tree Folio Release

`hfsplus_release_folio()` maps the metadata inode number to extents/catalog/attributes B-tree, then checks cached B-nodes that correspond to the folio:

- For node sizes at least page size, it maps one folio to one B-node index.
- For node sizes smaller than a page, it scans all B-node indices within that page.
- It refuses release if a cached node still has a nonzero refcount.
- If safe, it unhashes and frees cached nodes, then tries to free buffers.

This protects B-tree node cache consistency while allowing memory reclaim.

## Permission and Attribute Handling

- `hfsplus_get_perms()` validates catalog permission modes against expected directory/file types, applies mount UID/GID overrides, synthesizes default modes using mount umask when on-disk mode is absent, copies BSD user flags, and maps HFS+ immutable/append root flags to Linux `S_IMMUTABLE` and `S_APPEND`.
- `hfsplus_getattr()` adds `STATX_BTIME`, append/immutable/nodump attributes, and then calls `generic_fillattr()`.
- `hfsplus_fileattr_get()` maps Linux file attribute flags from inode state plus HFS+ nodump user flag.
- `hfsplus_fileattr_set()` rejects FS_XFLAG-style attributes and unsupported flags, maps immutable/append to inode flags, updates nodump in HFS+ user flags, updates ctime, and marks the inode dirty.

## File Operations

`hfsplus_file_operations` provides generic llseek/read/write/mmap/splice operations with HFS+-specific fsync/open/release/ioctl.

- `hfsplus_file_open()` redirects resource-fork opens to the main resource inode for open-count tracking and rejects non-largefile opens of files larger than `MAX_NON_LFS`.
- `hfsplus_file_release()` decrements the open count; when it reaches zero, it truncates allocation and, if the inode is dead, deletes the catalog entry from the hidden directory and deletes the inode.
- `hfsplus_setattr()` handles size changes with direct-I/O wait, contiguous expansion for grows, truncate for shrinks, timestamp updates, and generic attribute copying.
- `hfsplus_file_fsync()` writes data, syncs inode metadata to catalog/extents/attributes/allocation metadata files, prepares and commits the volume header, and issues a block-device flush unless `nobarrier` is set.

## Inode Lifecycle

- `hfsplus_new_inode()` allocates a VFS inode, assigns `next_cnid`, initializes ownership, timestamps, extent cache, open-dir state, resource-fork pointer, size/accounting fields, and operation tables based on mode. It increments file/folder counts, inserts into inode hash, marks dirty, and marks the volume header dirty.
- `hfsplus_delete_inode()` decrements file/folder counts, truncates regular files and symlinks when appropriate, and marks the volume header dirty.
- `hfsplus_inode_read_fork()` copies first extents from an on-disk fork, counts blocks in the first extent record, resets cached extents, sets allocation blocks, physical size, VFS size, `i_blocks`, and clump size.
- `hfsplus_inode_write_fork()` writes first extents, logical size, and allocated block count back into an on-disk fork.

## Catalog Record Serialization

- `hfsplus_cat_read_inode()` reads a catalog record from a B-tree cursor:
  - For `HFSPLUS_FOLDER`, validates entry length, reads folder record, applies permissions, sets link count, sets directory size to `2 + valence`, converts timestamps, stores create date and subfolder count, and installs directory ops.
  - For `HFSPLUS_FILE`, validates entry length, reads file record, chooses data/resource fork, applies permissions, sets regular/symlink/special operation tables, handles hard-link count stored in `permissions.dev`, initializes device special inodes, and converts timestamps.
  - Unexpected record types return `-EIO`.
- `hfsplus_cat_write_inode()` locates the main catalog record, skips unlinked main inodes, then writes updated folder or file metadata:
  - Directories: permissions, access/content/attribute dates, valence, optional subfolder count.
  - Resource fork inodes: resource fork fields only.
  - Regular file/symlink/special: data fork, permissions, file locked flag derived from immutable bits, timestamps.
  - It writes the catalog B-tree and sets catalog dirty bits on both catalog tree inode and target inode.

## Dependencies

Uses block/page-cache helpers, credential/idmap helpers, file attributes, HFS+ xattr declarations, extents, catalog, B-tree, and Unicode dentry callbacks.

## Research Notes

This file is the bridge between HFS+ catalog/fork metadata and Linux inode semantics. The most important behavior is that file data, extents, catalog records, allocation bitmap state, and volume header state are synchronized through separate metadata inodes and HFS+-specific dirty bits. Resource forks are treated specially: many operations redirect accounting or serialization to the main inode/resource relationship rather than treating the resource fork as an independent user-visible inode.
