# File Research: sources/os/linux/linux-stable/fs/exfat/dir.c

This file owns exFAT directory entry parsing, directory iteration, directory entry-set caching, name-entry initialization, checksum maintenance, empty-slot discovery validation, and volume-label directory entries.

Key elements:
- `exfat_readdir()` scans directory clusters, recognizes file/dir primary entries, gathers UTF-16 long names from secondary name entries, converts them to the mount charset, and advances `ctx->pos`.
- `exfat_iterate()` implements VFS directory iteration, emits dot entries, manages name buffers, and avoids holding `s_lock` across `dir_emit()`.
- `exfat_get_entry_type()` maps raw exFAT dentry type bytes to internal `TYPE_*` flags.
- `exfat_init_dir_entry()`, `exfat_init_ext_entry()`, and helpers create primary file, stream-extension, and filename entries.
- `exfat_update_dir_chksum()` computes and stores the entry-set checksum, skipping checksum bytes for the primary entry.
- `exfat_get_dentry()` maps a directory entry index to sector/offset, validates cluster allocation, reads the buffer, and returns an in-buffer pointer.
- `exfat_get_dentry_set()` reads a multi-entry set into `struct exfat_entry_set_cache`, including entries spanning sectors, and validates stream/name/secondary ordering.
- `exfat_get_empty_dentry_set()` validates a candidate empty range, tolerating deleted entries after unused entries for compatibility but detecting used-after-unused corruption.
- `exfat_find_dir_entry()` performs case-insensitive name lookup using stream name hash, filename entries, hints, and loop guards.
- `exfat_read_volume_label()` and `exfat_write_volume_label()` handle the root volume-label entry.

Important dependencies:
- Name conversion and comparison come from `nls.c`.
- Cluster walking and FAT/bitmap validation come from `fatent.c`/`balloc.c`.
- Namei create/rename/delete paths use entry-set creation, removal, and empty-slot search support here.
- Inode writeback uses `exfat_get_dentry_set_by_ei()` and checksum update to persist metadata.

Failure/edge behavior:
- Protects against deleted dentry access through `DIR_DELETED`.
- Caps directory scanning by `MAX_EXFAT_DENTRIES` and cluster-count loop guards.
- Frees clusters referenced by benign secondary entries when removing entry sets if those entries declare allocated data.
- `exfat_find_dir_entry()` updates parent hints both for next lookup and for future empty-entry allocation.
