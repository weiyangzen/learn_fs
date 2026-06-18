# File Research: sources/os/linux/linux-stable/fs/fat/namei_msdos.c

This file implements the `msdos` filesystem namespace operations using strict DOS 8.3 directory entries without VFAT long-name slots.

Key responsibilities:
- Format user names into 8.3 on-disk names.
- Provide dentry hash/compare operations based on formatted DOS names.
- Implement lookup, create, mkdir, unlink, rmdir, and rename.
- Handle `dotsOK` hidden-file behavior for non-VFAT mounts.
- Register the `msdos` filesystem type and fs_context operations.

Important functions:
- `msdos_format_name()` validates and converts names into 11-byte DOS format, rejecting invalid characters based on `check=` policy, uppercasing when required, handling extensions, spaces, leading dots, and the special first-byte `0xE5` to `0x05` mapping.
- `msdos_find()` formats a user name, scans the directory with `fat_scan()`, and applies hidden-dot conflict rules.
- `msdos_hash()` and `msdos_cmp()` make dcache operations compare by normalized DOS 8.3 form when possible.
- `msdos_lookup()` finds an entry under `s_lock` and builds or splices the inode.
- `msdos_add_entry()` builds one short directory entry with timestamps, attributes, hidden flag, start cluster, and size.
- `msdos_create()` rejects conflicts such as `foo` versus `.foo`, adds an entry, builds an inode, and instantiates the dentry.
- `msdos_mkdir()` allocates and initializes a new directory cluster, adds the parent entry, increments parent link count, and builds the child inode.
- `msdos_unlink()` and `msdos_rmdir()` remove entries, clear link counts, detach FAT inode hashes, and flush when needed.
- `do_msdos_rename()` handles replacement, cross-directory directory moves, `..` updates, hidden-attribute changes for dot aliases, link-count adjustments, and rollback on sync failure.
- `msdos_rename()` validates flags, formats old/new names, computes hidden-dot state, and delegates to `do_msdos_rename()`.

Operations and registration:
- `msdos_dir_inode_operations` wires VFS namespace operations to shared FAT setattr/getattr/update_time.
- `setup()` installs msdos directory ops and dentry ops and sets `SB_NOATIME`.
- The module registers `msdos_fs_type` with `fat_fill_super()` and `fat_parse_param(..., false)`.

Failure behavior:
- Invalid names generally map to `-EINVAL` or lookup `-ENOENT`.
- Rename rollback attempts to restore inode attachments, dotdot entries, and target entries; serious partial failures are reported as filesystem corruption.

Research relevance:
- This is the short-name-only namespace personality for FAT. It shows how the common FAT directory layer is adapted to legacy DOS naming rules.
