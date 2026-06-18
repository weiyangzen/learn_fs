# File Research: sources/os/linux/linux-stable/fs/fat/inode.c

This file implements the core FAT superblock, inode, address-space, mount-option, and module lifecycle logic.

Key responsibilities:
- Map file blocks for buffered I/O, direct I/O, writeback, bmap, and truncation.
- Manage FAT-private inode caches keyed by directory-entry position.
- Build VFS inodes from on-disk directory entries.
- Serialize inode metadata back to FAT directory entries.
- Parse mount options for both `msdos` and `vfat`.
- Read and validate boot-sector BPB data, including optional DOS 1.x floppy defaults.
- Fill the superblock, root inode, synthetic FAT/FSINFO inodes, NLS tables, export operations, and filesystem geometry.
- Manage FAT inode slab cache and module init/exit.

Important I/O functions:
- `fat_add_cluster()` allocates one cluster and appends it to an inode chain.
- `__fat_get_block()` maps or allocates a block, using `mmu_private` to prevent hole creation and adding clusters at cluster boundaries.
- `fat_write_begin()` / `fat_write_end()` integrate FAT allocation with buffered writes and set archive/time metadata.
- `fat_direct_IO()` allows direct reads/writes only when writes do not need to extend `mmu_private`; otherwise it falls back to buffered I/O.
- `_fat_bmap()` protects bmap against truncation with `truncate_lock`.
- `fat_block_truncate_page()` zeroes partial blocks before truncation.

Important inode functions:
- `fat_attach()` and `fat_detach()` maintain the on-disk-position hash and optional directory-start-cluster hash for NFS.
- `fat_iget()` finds an inode by on-disk directory-entry position.
- `fat_fill_inode()` converts a `msdos_dir_entry` into VFS inode mode, operations, size, blocks, timestamps, attributes, and cluster starts.
- `fat_build_inode()` creates or reuses an inode for a directory entry and attaches it to FAT hashes.
- `fat_evict_inode()` frees clusters for unlinked files, trims unused fallocated EOF blocks, invalidates metadata buffers, clears cluster cache, and detaches hashes.
- `__fat_write_inode()` updates the backing directory entry with size, attributes, start cluster, mtime, and VFAT atime/ctime fields.

Important mount/superblock functions:
- `fat_parse_param()` handles shared, msdos-specific, and vfat-specific mount options.
- `fat_init_fs_context()` initializes default mount options.
- `fat_read_bpb()` validates normal FAT BPB fields.
- `fat_read_static_bpb()` supplies defaults for recognized DOS 1.x floppy images when requested.
- `fat_fill_super()` allocates `msdos_sb_info`, applies options, reads BPB/FSINFO, computes FAT layout and cluster counts, loads NLS tables, creates synthetic/root inodes, chooses export operations, marks the volume dirty, and installs the root dentry.
- `fat_put_super()` clears dirty state and releases synthetic inodes and NLS resources.
- `fat_statfs()` reports free space, counting clusters on demand.

State and locking:
- `s_lock` serializes high-level FAT operations.
- `inode_hash_lock` protects `i_pos` attachment and write_inode races.
- `dir_hash_lock` supports NFS parent reconstruction.
- `truncate_lock` protects bmap against truncate.
- `nfs_build_inode_lock` serializes inode construction in no-stale NFS mode.

Failure behavior:
- Invalid BPB geometry, unsupported logical sector size, missing codepage/iocharset, bad root inode creation, or invalid cluster counts fail mount.
- Dirty volumes produce warnings but remain mountable.
- Writeback retries when inode `i_pos` changes during rename.

Research relevance:
- This is the central FAT core. It connects mount-time geometry discovery, VFS inode lifecycle, data I/O, metadata serialization, option parsing, and module-global cache setup.
