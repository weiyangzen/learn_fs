# File Research: sources/os/linux/linux/fs/ntfs/unistr.c

Read coverage: complete file, 477 lines.

This file implements Unicode and NLS string handling for the legacy NTFS driver. All NTFS strings are treated as little-endian UTF-16.

Key functions:
- `ntfs_are_names_equal()` and `ntfs_names_are_equal()` compare UTF-16 names, optionally case-insensitive via an upcase table.
- `ntfs_collate_names()` implements NTFS filename collation with invalid-character detection for `"`, `*`, `<`, `>`, and `?`.
- `ntfs_ucsncmp()` / `ntfs_ucsncasecmp()` compare little-endian Unicode strings with or without upcasing.
- `ntfs_file_compare_values()` adapts filename attributes to collation.
- `ntfs_nlstoucs()` converts mount-NLS or UTF-8 input names into little-endian UTF-16, allocating from `ntfs_name_cache` for normal names or `kvmalloc()` for longer requested limits.
- `ntfs_ucstonls()` converts UTF-16 names back to the mounted NLS/UTF-8 encoding, allocating/growing output when needed.
- `ntfs_ucsndup()` duplicates bounded UTF-16 strings.

Integration:
- Depends on `struct ntfs_volume` NLS settings, `ntfs_name_cache`, UTF conversion helpers, and the volume upcase table.
- Used by path lookup, directory indexing/collation, label handling, and filename conversion between VFS byte strings and NTFS UTF-16.

Risks:
- Error handling must release the right allocator family: slab cache for normal NTFS names and `kvfree()` for larger buffers.
- Name length limits are enforced at conversion time; callers must pass correct maximum lengths for filenames versus labels.
- Collation only validates invalid characters in `name1`, matching its documented contract.
