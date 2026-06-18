# File Research: sources/local-fs/btrfs-progs/mkfs/rootdir.c

## Role

`mkfs/rootdir.c` implements `mkfs.btrfs --rootdir`. It walks a host directory tree and materializes it into the newly created Btrfs filesystem, preserving metadata such as modes, ownership, timestamps, xattrs, symlinks, hardlinks, sparse holes, special-file types, selected inode flags, and requested subvolume boundaries. It also estimates image size for rootdir creation and can shrink a populated single-device image down to the last used device extent.

## Traversal State

The file uses process-global state for one rootdir import:

- `current_path`: stack of current Btrfs directory inodes during `nftw()` preorder traversal.
- `g_trans`: active transaction used by callbacks.
- `g_subvols`: remaining requested subvolume definitions.
- `g_inode_flags_list`: remaining requested inode-flag overrides.
- `next_subvol_id`: object id allocator for requested subvolumes.
- `default_subvol_id`: selected default subvolume id.
- `g_compression` and `g_compression_level`: rootdir compression mode.
- `g_do_reflink`: whether file data should be cloned with `FICLONERANGE`.
- `hardlink_root`: rb-tree keyed by `(st_dev, st_ino, btrfs_root)` for hardlink reconstruction without crossing subvolume boundaries.
- checksum ioctl cache:
  - `g_get_csums_supported`
  - `g_last_csums_dev`
  - `g_last_csums_dev_ok`

## Key Data Structures

- `struct inode_entry` stores a Btrfs root pointer and inode number for the current path stack.
- `struct hardlink_entry` maps host inode identity to the first Btrfs inode created for that file inside the same subvolume root.
- `struct rootdir_path` tracks traversal depth and directory stack.
- `struct source_descriptor` carries file fd, buffers, size, path, optional compression work buffers, and source device id into extent-writing helpers.

## Validation API

- `btrfs_mkfs_validate_subvols()` canonicalizes each requested subvolume path, verifies it exists and is a directory, stores its host `(st_dev, st_ino)`, and rejects duplicate subvolume specifications.
- `btrfs_mkfs_validate_inode_flags()` canonicalizes each flagged path, verifies it exists, stores `(st_dev, st_ino)`, and rejects duplicate flag records for the same inode.

These validation passes run before filesystem creation is committed to rootdir population.

## Metadata Import

- `stat_to_inode_item()` converts host `struct stat` into a Btrfs inode item, copying uid/gid/mode and atime/ctime/mtime seconds.
- `add_xattr_item()` copies xattrs with `llistxattr()` and `lgetxattr()` into Btrfs xattr items, ignoring unsupported-xattr filesystems.
- `add_symbolic_link()` reads the symlink target and stores it as an inline extent.
- `ftype_to_btrfs_type()` maps POSIX file modes to Btrfs dir item types.
- `update_inode_flags()` applies requested `nodatacow` and `nodatasum`; `nodatacow` implies `nodatasum` for regular files.
- `search_and_update_inode_flags()` applies and removes the matching inode-flag record by host inode identity.

## File Data Import

Regular file content flows through `add_file_items()` and `add_file_item_extent()`.

Supported behavior:

- Empty files need no extents.
- Small files below inline limits are inserted as inline extents, optionally compressed if that reduces size.
- Larger files are split into at most 1 MiB extents (`MAX_EXTENT_SIZE`) to fit mkfs-time small block groups.
- Sparse holes are detected with `SEEK_DATA`/`SEEK_HOLE` and represented as Btrfs hole extents when aligned.
- Data checksums are inserted unless inode flags disable data checksumming.
- Optional compression supports zlib, LZO, and ZSTD when compiled in.
- Optional reflink writes use `FICLONERANGE` from the source fd into the destination device range after logical-to-physical mapping.
- If the source is Btrfs and checksum settings match, the code tries `BTRFS_IOC_GET_CSUMS` to import existing checksums instead of recomputing them.

Important helpers:

- `insert_reserved_file_extent()` inserts extent-tree records, removes allocated space from the free-space tree, inserts the file extent, updates inode nbytes, and increments extent refs. It handles disk bytenr 0 as a hole extent.
- `read_from_source()` performs aligned pread loops into the staging buffer.
- `try_compressed_write()` compresses a range, writes compressed bytes, creates csums for compressed sectors, sets inode compression flags, and inserts a compressed file extent.
- `do_reflink_write()` maps Btrfs logical destination ranges to physical device ranges and clones source ranges into those offsets.
- zlib/LZO/ZSTD helpers implement both regular compressed extents and inline compressed extents.

## Directory, Subvolume, and Hardlink Import

`ftw_add_inode()` is the main `nftw()` callback.

- The rootdir itself updates the existing fs-tree root inode and initializes `current_path`.
- Before processing each entry, the path stack is popped until it matches the traversal depth.
- If a directory matches a requested subvolume `(st_dev, st_ino)`, `ftw_add_subvol()` creates a Btrfs subvolume, links it under the current parent, updates its root inode metadata/xattrs, marks it default if requested, and pushes it onto the path stack.
- For non-directory hardlinked files, the rb-tree allows later links to reuse the first Btrfs inode in the same root. Cross-subvolume hardlinks are intentionally not recreated as hardlinks.
- New inodes are allocated with `btrfs_find_free_objectid()`, inserted, linked into the parent directory, decorated with xattrs, and then populated according to type.
- Directories are pushed onto the traversal stack after insertion.
- Regular files call `add_file_items()` and then rewrite the inode item with updated nbytes/flags.
- Symlinks call `add_symbolic_link()` and then update the inode item.

`set_default_subvolume()` updates the root-tree `"default"` dir item to point at the requested default subvolume and sets the default-subvol incompat feature bit.

`btrfs_mkfs_fill_dir()` is the public import entry point. It validates compression availability/default levels, initializes global traversal state, runs `nftw(source_dir, ftw_add_inode, 32, FTW_PHYS)`, drains the path stack, sets the default subvolume if requested, and frees remaining hardlink records.

## Size Estimation

`btrfs_mkfs_size_dir()` estimates the minimum target size for `--rootdir`.

- It walks the source with `nftw(..., FTW_PHYS)`.
- `ftw_add_entry_size()` counts every inode and sums regular-file data.
- `add_data_size()` prefers allocated blocks for sparse files when `SEEK_DATA` works; otherwise it falls back to rounded file size.
- Metadata estimate is `inode_count * (PATH_MAX * 3 + sectorsize) + data_size / 8`.
- Data and metadata chunk estimates account for minimal chunk thresholds and DUP multipliers.
- Returned size is `min_dev_size + estimated_data_extra + estimated_metadata_extra`.

The estimate intentionally over-allocates so population is less likely to hit ENOSPC; `--shrink` can reduce image size afterward.

## Shrink Support

- `get_device_extent_end()` finds the exclusive end of the last device extent for a devid.
- `set_device_size()` updates in-memory device size, chunk-tree device item size, super total bytes, and commits the change.
- `btrfs_mkfs_shrink_fs()` only supports single-device filesystems. It computes the last used device extent, verifies sectorsize alignment, updates device/super sizes, and truncates the backing file if it is a regular file and `shrink_file_size` is true.

## Error Handling and Edge Cases

- `FTW_DNR` and `FTW_NS` during sizing abort early with `-EPERM`.
- xattr unsupported cases are nonfatal.
- Compression failure due to poor ratio returns `-E2BIG` and falls back to uncompressed data; first-block compression failure can mark the inode `NOCOMPRESS`.
- Reflink and checksum import require block-aligned ranges; partial tail blocks fall back to normal read/write/checksum behavior.
- `BTRFS_IOC_GET_CSUMS` support is cached; `ENOTTY` disables future attempts.
- Hardlink records are removed once all host-reported links are found, but links outside rootdir mean records may remain until final rb-tree cleanup.
- The traversal deliberately uses `FTW_PHYS`, so symlinks are copied as symlinks rather than followed.

## Research Notes

This file is the rootdir materialization engine. It bridges host filesystem metadata and Btrfs on-disk item construction, with special care for subvolume boundaries, sparse file layout, compression compatibility, checksumming, and post-population image minimization.
