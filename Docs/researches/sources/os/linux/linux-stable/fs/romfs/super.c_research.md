# File Research: sources/os/linux/linux-stable/fs/romfs/super.c

## Purpose

Implements the Linux ROMFS filesystem driver, including read-only inode lookup, directory iteration, file/symlink folio reads, superblock validation, block/MTD mount plumbing, inode-cache lifecycle, and module registration.

## Main Responsibilities

- Defines ROMFS inode mode/type mapping and dentry type mapping from ROMFS file-header type bits.
- Implements `romfs_read_folio()` for reading regular-file and symlink data from the underlying ROMFS image via `romfs_dev_read()`, with zero-fill beyond EOF.
- Implements directory traversal:
  - `romfs_readdir()` walks the ROMFS linked list of directory entries, follows hard-link entry inode numbers for `dir_emit()`, and emits VFS dentry types.
  - `romfs_lookup()` scans directory entries by name using `romfs_dev_strcmp()` and returns `d_splice_alias()` on a resolved inode.
- Implements `romfs_iget()`:
  - Follows ROMFS hard-link file-header chains before instantiating the inode.
  - Computes metadata and data offsets from fixed header size plus padded filename length.
  - Sets inode mode, size, timestamps, block count, inode/file operations, address-space ops, and special inode device numbers.
- Implements superblock operations:
  - `romfs_alloc_inode()` and `romfs_free_inode()` use the ROMFS inode slab cache.
  - `romfs_statfs()` reports ROMFS magic, name length, block size, total image size, and fsid based on block device or MTD device identity.
  - `romfs_reconfigure()` forces read-only remount.
- Implements mount-time validation in `romfs_fill_super()`:
  - Sets block size, maximum file size, flags, magic, noatime, readonly, time range, and super ops.
  - Reads the first 512 bytes, validates ROMFS magic words, image size, MTD bounds, and initial checksum.
  - Logs image name and storage backend, computes root header position, and creates the root dentry.
- Supports block and MTD backends through `romfs_get_tree()` using `get_tree_mtd()` and/or `get_tree_bdev()` depending on configuration.
- Implements filesystem registration and cleanup through `init_romfs_fs()` and `exit_romfs_fs()`.

## Key Data/Control Flow

- ROMFS inode numbers are image offsets masked by `ROMFH_MASK`.
- Directory entries are a singly linked list through the `next` file-header field.
- Regular file data starts at `ROMFS_I(inode)->i_dataoffset`, computed from the header plus padded filename.
- The root inode position is derived from the superblock header and volume-name length.
- The filesystem is always mounted read-only with no atime updates.

## Integration Notes

- Depends on ROMFS device helpers from the ROMFS internal layer, especially `romfs_dev_read()`, `romfs_dev_strnlen()`, `romfs_dev_strcmp()`, and `romfs_maxsize()`.
- Uses VFS helpers such as `iget_locked()`, `unlock_new_inode()`, `d_make_root()`, `d_splice_alias()`, `generic_file_llseek()`, `generic_read_dir()`, and `page_symlink_inode_operations`.
- Uses MTD/block mount helpers and explicitly releases MTD and block device references in `romfs_kill_sb()`.

## Correctness and Risk Notes

- Mount validation relies on the initial ROMFS checksum over `min(image_size, 512)`.
- `romfs_iget()` has an inline note that per-inode checksum validation is not performed there.
- Directory iteration returns success even if traversal ended through the normal `out` path; underlying read errors end iteration rather than surfacing a negative return from `romfs_readdir()`.
- Read paths convert any negative backend read result to `-EIO`.
