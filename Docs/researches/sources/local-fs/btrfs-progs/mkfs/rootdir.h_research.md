# File Research: sources/local-fs/btrfs-progs/mkfs/rootdir.h

## Role

`mkfs/rootdir.h` is the public interface between the main mkfs command and the `--rootdir` implementation in `rootdir.c`. It declares the option data structures used by `main.c` and the functions used to validate, size, populate, and shrink a rootdir-created filesystem.

## Public Constants

- `ZLIB_BTRFS_DEFAULT_LEVEL` is `3`.
- `ZLIB_BTRFS_MAX_LEVEL` is `9`.
- `ZSTD_BTRFS_DEFAULT_LEVEL` is `3`.
- `ZSTD_BTRFS_MAX_LEVEL` is `15`.

These are used by both option parsing and rootdir compression setup.

## Public Types

`struct rootdir_subvol` represents one `--subvol` request.

Fields:

- `list`: intrusive list node.
- `dir[PATH_MAX]`: path inside the source directory.
- `st_dev`, `st_ino`: host inode identity filled during validation.
- `is_default`: whether this subvolume becomes the default subvolume.
- `readonly`: whether the created subvolume is read-only.

`struct rootdir_inode_flags_entry` represents one `--inode-flags` request.

Fields:

- `list`: intrusive list node.
- `inode_path[PATH_MAX]`: path inside the source directory.
- `st_dev`, `st_ino`: host inode identity filled during validation.
- `nodatacow`: request `BTRFS_INODE_NODATACOW`.
- `nodatasum`: request `BTRFS_INODE_NODATASUM`.

Both structures store host inode identity because later traversal matches by `(st_dev, st_ino)`, not by raw path string.

## Public Functions

- `btrfs_mkfs_validate_subvols(source_dir, subvols)` validates requested subvolume paths, ensures they are existing directories, records host inode identities, and rejects duplicates.
- `btrfs_mkfs_validate_inode_flags(source_dir, inode_flags)` validates requested inode-flag paths, records host inode identities, and rejects duplicates.
- `btrfs_mkfs_fill_dir(trans, source_dir, root, subvols, inode_flags_list, compression, compression_level, do_reflink)` populates the new filesystem from the host directory tree.
- `btrfs_mkfs_size_dir(dir_name, sectorsize, min_dev_size, meta_profile, data_profile)` estimates the target size needed before rootdir import.
- `btrfs_mkfs_shrink_fs(fs_info, new_size_ret, shrink_file_size)` shrinks a populated single-device filesystem/image to the last used device extent.

## Dependencies

The header exposes only forward declarations for `struct btrfs_fs_info` and `struct btrfs_root`, includes list support, and depends on Btrfs compression enum definitions from `kernel-shared/compression.h`.

## Research Notes

This header is intentionally narrow. It gives `main.c` enough structure to collect command-line rootdir requests, validate them before formatting, and then hand all import details to `rootdir.c`.
