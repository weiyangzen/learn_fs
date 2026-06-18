# File Research: sources/local-fs/linux-apfs-rw/inode.c

## Purpose
Implements APFS VFS inode lifecycle, page-cache read/write integration, inode record serialization, dstream and crypto-state bookkeeping, orphan cleanup, metadata updates, and APFS-specific ioctls.

## Main Responsibilities
- Provides address-space operations for regular files, including `read_folio`/`readpage`, readahead, `write_begin`, and `write_end`.
- Performs APFS copy-on-write write setup by reading existing mapped buffers, clearing mappings, then allocating replacement blocks with `apfs_get_new_block`.
- Creates, updates, and deletes catalog inode records and inode xfields for names, dstreams, sparse-byte counts, and device IDs.
- Tracks APFS dstream records and reference counts, including clone-related exclusive dstream creation through `apfs_inode_create_exclusive_dstream()`.
- Manages encrypted-volume crypto-state records and private file keys through APFS ioctls.
- Creates and populates VFS inodes from catalog queries in `apfs_iget()`.
- Handles setattr, truncate, timestamp updates, file attributes, BSD flags, immutable/append/nodump state, and statx birth time.
- Cleans orphan inodes synchronously for trivial cases and asynchronously through `apfs_orphan_cleanup_work()` for large or partial deletions.

## Key Functions
- `apfs_iget()`: looks up an inode catalog record, fills VFS/APFS inode fields, checks dstream sharing, and unlocks a new inode.
- `apfs_inode_from_query()`: parses an APFS inode record, timestamps, ownership, BSD flags, dstream xfields, sparse bytes, rdev, and compressed-file state.
- `apfs_update_inode()`: flushes extent cache, updates name/dstream/sparse xfields, and writes changed inode metadata back into the catalog node.
- `apfs_new_inode()` and `apfs_create_inode_rec()`: allocate a new VFS inode and persist its initial APFS catalog record.
- `apfs_setattr()` / `apfs_setsize()`: validate and apply VFS attribute changes, using APFS transactions and truncation paths.
- `apfs_delete_inode()`, `apfs_clean_single_orphan()`, `apfs_clean_orphans()`: remove xattrs, extents, dstream records, catalog records, and orphan links.
- `apfs_dir_ioctl()` / `apfs_file_ioctl()`: dispatch APFS key-class, PFK, and snapshot ioctls.

## Dependencies
Uses catalog b-tree operations, extent/truncate logic, xattr deletion, compression helpers, transaction joining/commit/abort, dstream extent cloning, APFS superblock counters, VFS inode/page-cache APIs, and kernel-version compatibility branches.

## Notes
The file is heavily version-gated for Linux API changes from older page APIs through folios, idmapped mounts, fileattr APIs, and timestamp helpers. Several TODOs mark incomplete clone support, `write_inode()` uncertainty, sparse xfield cleanup policy, and crypto-record deletion semantics.
