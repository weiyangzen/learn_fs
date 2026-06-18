# File Research: sources/os/linux/linux/fs/exfat/dir.c

## Purpose
Implements directory entry parsing, directory iteration, entry-set caching/writing, directory-entry checksums, free-slot validation, name matching support, subdirectory counting, and volume-label read/write.

## Main Interfaces
- File ops: `exfat_dir_operations`
- Entry helpers: `exfat_get_entry_type`, `exfat_get_dentry`, `exfat_get_dentry_set`, `exfat_get_empty_dentry_set`, `exfat_put_dentry_set`
- Mutation helpers: `exfat_init_dir_entry`, `exfat_init_ext_entry`, `exfat_remove_entries`, `exfat_update_dir_chksum`
- Search/count helpers: `exfat_find_dir_entry`, `exfat_count_dir_entries`
- Volume label: `exfat_read_volume_label`, `exfat_write_volume_label`

## Key Data Flow
Directory records are handled as entry sets: file entry, stream extension, then one or more filename entries, optionally followed by secondary entries. `exfat_readdir()` walks a directory chain, extracts UTF-16 name pieces, converts them through NLS/UTF-8 helpers, and emits VFS directory entries outside `s_lock`.

`__exfat_get_dentry_set()` loads all sectors covering an entry set into buffer heads, using inline storage for common cases and dynamic allocation if needed. `exfat_get_dentry_set()` validates the expected file/stream/name/secondary sequence. Modified entry sets are flushed by `exfat_put_dentry_set()`.

`exfat_find_dir_entry()` scans dentries with name-hash prefiltering, UTF-16 case-insensitive comparison, hint updates, empty-slot hints, rewind support, and loop guards.

## Dependencies
Uses allocation/FAT chain traversal, NLS conversion, checksum helpers, buffer heads, inode hint fields, and the global exFAT superblock lock.

## Notable Invariants And Risks
- Entry-set validation protects against malformed secondary-entry ordering.
- Deleting an entry also frees allocatable benign-secondary clusters.
- Directory iteration must drop `s_lock` before `dir_emit()`.
- Volume-label lookup reuses root empty-entry hints when no label exists.
