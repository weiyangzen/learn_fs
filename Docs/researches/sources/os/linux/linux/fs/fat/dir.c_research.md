# File Research: sources/os/linux/linux/fs/fat/dir.c

## Purpose
Implements FAT directory traversal, name parsing, directory-entry search, readdir/ioctl readdir, directory entry allocation/removal, and new-directory initialization.

## Main Responsibilities
- Reads directory entries through `fat_get_entry()` and physical mappings from `fat_bmap()`.
- Parses short 8.3 names and VFAT long-name slot chains.
- Implements `iterate_shared` via `fat_readdir()`.
- Supports legacy VFAT directory ioctls returning short or short+long names.
- Searches directories by name, short name, or starting cluster.
- Adds/removes directory entry slot sequences.
- Allocates and zeroes clusters for new directories or directory growth.

## Key Interfaces
- `fat_search_long()`: searches a directory by display/input name, comparing both short and long names.
- `fat_dir_empty()`: checks that a directory contains no entries other than `.` and `..`.
- `fat_subdirs()`: counts subdirectories for link-count setup.
- `fat_scan()` / `fat_scan_logstart()`: find a short-name entry or entry with a given starting cluster.
- `fat_get_dotdot_entry()`: locates `..` in a directory.
- `fat_alloc_new_dir()`: allocates a cluster and writes `.` / `..`.
- `fat_add_entries()`: writes one or more short/VFAT slots into free directory space or extends the directory.
- `fat_remove_entries()`: marks a short entry and its long-name slots deleted.
- `fat_dir_operations`: file operations for directories.

## Important Behavior
`fat_parse_long()` validates VFAT slot ordering, slot count, checksum, and associated short entry. If checksum validation fails, it still allows the short name but clears `nr_slots`, preventing the long name from being used.

`fat_parse_short()` handles 8.3 decoding, hidden-dot presentation for msdos mounts, case display flags, NLS conversion, UTF-8 conversion through `fat_uni_to_x8()`, and the special 0x05/0xE5 deleted-entry convention.

`__fat_readdir()` serializes directory reads with `sbi->s_lock`, fakes `.` and `..` for root, handles invalid offsets, skips volume/free/deleted entries, and emits stable inode numbers by trying `fat_iget()` for existing inodes or falling back to `iunique()`.

`fat_add_entries()` is staged for consistency: it first fills existing free slots if possible, syncs long slots before short slots for dirsync, then allocates and chains new clusters only if needed. On failure after partial insertion it removes any slots it just wrote.

## Dependencies
Depends on `cache.c` for `fat_bmap()`, `fatent.c`/`misc.c` for cluster allocation and time conversion, `inode.c` for `fat_iget()` and inode build/sync helpers, and `fat.h` structures/constants.

## Research Notes
Ordering matters: deletion marks the short entry first, making the file invisible before long-name cleanup. Creation writes long-name slots before the short entry, so incomplete creation is less likely to expose a valid file. Directory cluster zeroing uses buffer locking to avoid races with userspace reads through the block device.
