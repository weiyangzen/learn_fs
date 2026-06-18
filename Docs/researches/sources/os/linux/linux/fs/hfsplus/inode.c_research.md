# File Research: sources/os/linux/linux/fs/hfsplus/inode.c

## Role

Implements HFS+ inode handling and regular-file VFS operations. It connects Linux page-cache/block-mapping helpers to HFS+ extent mapping, manages file open/release semantics, serializes and deserializes catalog file/folder records, maps HFS+ permissions and user flags to Linux inode/file attributes, and participates in metadata sync.

## Address-Space and Dentry Operations

- `hfsplus_read_folio()` uses `block_read_full_folio()` with `hfsplus_get_block`.
- `hfsplus_write_begin()` uses `cont_write_begin()` and tracks `HFSPLUS_I(mapping->host)->phys_size`; failed extending writes call `hfsplus_write_failed()`.
- `hfsplus_write_failed()` truncates page cache and HFS+ file allocation back to `i_size` if a failed write allocated beyond EOF.
- `hfsplus_bmap()` delegates to `generic_block_bmap()`.
- `hfsplus_direct_IO()` delegates to `blockdev_direct_IO()` and trims blocks after failed extending direct writes.
- `hfsplus_writepages()` delegates to `mpage_writepages()`.
- `hfsplus_btree_aops` is used by metadata B-tree inodes and adds `release_folio = hfsplus_release_folio`.
- `hfsplus_aops` is used by regular file and symlink data mappings.
- `hfsplus_dentry_operations` wires Unicode-aware HFS+ dentry hash and compare functions.

## B-tree Folio Release

`hfsplus_release_folio()` maps metadata inode numbers to the corresponding extents, catalog, or attributes tree. It then checks cached B-nodes associated with the folio:

- for node sizes at least page size, it maps one folio to one B-node index;
- for node sizes smaller than a page, it scans all node indices inside the page;
- it refuses release if a cached node still has a nonzero refcount;
- if safe, it unhashes and frees cached nodes, then calls `try_to_free_buffers()`.

This protects B-tree cache consistency during memory reclaim.

## Permission and Attribute Handling

- `hfsplus_get_perms()` validates catalog permission modes against directory/file expectations, applies mount UID/GID overrides, synthesizes default modes with mount umask when on-disk mode is absent, copies BSD user flags, and maps HFS+ immutable/append root flags to Linux `S_IMMUTABLE` and `S_APPEND`.
- `hfsplus_getattr()` adds `STATX_BTIME`, append/immutable/nodump attributes, and then calls `generic_fillattr()`.
- `hfsplus_fileattr_get()` reports immutable, append, nodump, and, in this `linux` tree, `FS_CASEFOLD_FL` when the superblock has `HFSPLUS_SB_CASEFOLD` set.
- `hfsplus_fileattr_set()` rejects FS_XFLAG-style attributes and unsupported flags, maps immutable/append to inode flags, updates HFS+ nodump user flags, updates ctime, and marks the inode dirty. It accepts `FS_CASEFOLD_FL` as a no-op only when the mounted volume is already casefolded, so read-modify-write tools such as `chattr` can round-trip attributes without trying to change a mount-time HFS+ property.

## File Operations

`hfsplus_file_operations` provides generic llseek/read/write/mmap/splice operations plus HFS+-specific fsync/open/release/ioctl.

- `hfsplus_file_open()` redirects resource-fork opens to the main resource inode for open-count tracking and rejects non-largefile opens for files larger than `MAX_NON_LFS`.
- `hfsplus_file_release()` decrements the open count; when it reaches zero, it truncates allocation and, for dead inodes, deletes the catalog entry from the hidden directory and deletes the inode.
- `hfsplus_setattr()` handles size changes with direct-I/O wait, contiguous expansion for grows, truncate for shrinks, timestamp updates, generic attribute copying, and inode dirtiness.
- `hfsplus_file_fsync()` writes data, syncs inode metadata to catalog/extents/attributes/allocation metadata files, prepares and commits the volume header, and issues a block-device flush unless `nobarrier` is set.

## Inode Lifecycle

- `hfsplus_new_inode()` allocates a VFS inode, assigns `next_cnid`, initializes owner/timestamps/extent cache/open-dir state/resource-fork pointer/accounting fields, selects operations based on mode, increments file/folder counts, inserts into the inode hash, marks dirty, and marks the volume header dirty.
- `hfsplus_delete_inode()` decrements file/folder counts, truncates regular files and symlinks when appropriate, and marks the volume header dirty.
- `hfsplus_inode_read_fork()` copies first extents from an on-disk fork, counts blocks in the first extent record, resets cached extents, sets allocation blocks, physical size, VFS size, `i_blocks` accounting, and clump size.
- `hfsplus_inode_write_fork()` writes first extents, logical size, and allocated block count back into an on-disk fork.

## Catalog Record Serialization

- `hfsplus_cat_read_inode()` reads a catalog record from a B-tree cursor:
  - `HFSPLUS_FOLDER`: validates entry length, reads folder record, applies permissions, sets link count, sets directory size to `2 + valence`, converts timestamps, stores create date and optional subfolder count, and installs directory ops.
  - `HFSPLUS_FILE`: validates entry length, reads file record, chooses data or resource fork, applies permissions, sets regular/symlink/special operation tables, handles hard-link count stored in `permissions.dev`, initializes special inodes, and converts timestamps.
  - unexpected record types return `-EIO`.
- `hfsplus_cat_write_inode()` locates the main catalog record, skips unlinked main inodes, and writes updated folder/file metadata:
  - directories: permissions, access/content/attribute dates, valence, optional subfolder count;
  - resource fork inodes: resource fork fields only;
  - regular file/symlink/special: data fork, permissions, file locked flag derived from immutable bits, timestamps.
  - it writes the catalog B-tree and marks catalog dirty bits on both catalog-tree inode and target inode.

## Dependencies

Uses block/page-cache helpers, direct-I/O helpers, credential/idmap helpers, file-attribute APIs, HFS+ xattr declarations, extents, catalog, B-tree, and Unicode dentry callbacks.

## Research Notes

This file is the bridge between HFS+ catalog/fork metadata and Linux inode semantics. File data, extents, catalog records, allocation bitmap state, and volume header state are synchronized through separate metadata inodes plus HFS+-specific dirty bits. Resource forks are not treated as fully independent user-visible files; open counts and serialization route through the main inode/resource relationship.
