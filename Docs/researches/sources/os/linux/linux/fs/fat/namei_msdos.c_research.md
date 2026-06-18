# File Research: sources/os/linux/linux/fs/fat/namei_msdos.c

## Purpose
Implements the `msdos` filesystem namespace layer: 8.3-only name formatting, lookup, create, mkdir, unlink, rmdir, rename, dentry hashing/comparison, mount registration, and fs_context hooks.

## Main Responsibilities
- Converts user names to strict/normal/relaxed MS-DOS 8.3 names.
- Handles `dotsOK` hidden-file dot presentation.
- Provides msdos dentry hash/compare operations based on formatted 8.3 names.
- Implements directory inode operations for creation, deletion, lookup, and rename.
- Registers the `msdos` filesystem type.

## Key Interfaces
- `msdos_format_name()`: validates and formats user names into 11-byte 8.3 form.
- `msdos_find()`: formats a name and scans the directory.
- `msdos_lookup()`: finds and builds an inode, then splices aliases.
- `msdos_add_entry()`: writes a single short directory entry.
- `msdos_create()`, `msdos_mkdir()`, `msdos_unlink()`, `msdos_rmdir()`: namespace operations.
- `do_msdos_rename()` / `msdos_rename()`: rename implementation.
- `msdos_init_fs_context()`: initializes shared FAT context with `is_vfat=false`.

## Important Behavior
`msdos_format_name()` rejects invalid characters according to mount `check=` mode, uppercases lowercase unless `nocase`, handles leading dot names only with `dotsOK`, prohibits trailing spaces, and maps first-byte 0xE5 to 0x05.

`msdos_find()` applies the hidden attribute distinction for `dotsOK`: `.foo` and `foo` can map to the same 8.3 short name but are distinguished by `ATTR_HIDDEN`.

Create and mkdir explicitly reject conflicts between dot-hidden and non-hidden forms by scanning the formatted short name before insertion.

Rename is careful with directories: it updates `..` when moving across parents, adjusts link counts, detaches and reattaches inode hash positions, handles the special `foo` to `.foo` hidden-attribute-only rename, and tries rollback paths if inode or dotdot updates fail.

## Dependencies
Uses shared FAT directory, inode, time, sync, and attribute helpers. `setup()` installs `msdos_dir_inode_operations` and `msdos_dentry_operations`, then enables `SB_NOATIME`.

## Research Notes
The msdos namespace is short-name-only and lacks VFAT long-name slot management. Most complexity comes from legacy name validation and hidden-dot compatibility.
