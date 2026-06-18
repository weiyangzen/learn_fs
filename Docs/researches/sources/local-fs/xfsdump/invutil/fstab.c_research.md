# File Research: sources/local-fs/xfsdump/invutil/fstab.c

Implements invutil operations for viewing, pruning, importing, deleting, and committing fstab entries.

Key functions:
- `generate_fstab_menu()` opens/maps a fstab file, creates one menu node per filesystem, and then generates child invidx menus.
- `fstab_highlight()` displays device and UUID in the info window.
- `fstab_prune()` matches entries by mount point or UUID.
- `fstab_commit()` deletes native entries by shifting mmap contents and decrementing counters, or imports entries after committing children.
- `find_matching_fstab()` avoids duplicate imports.
- `remmap_fstab()` grows/remaps the fstab file and rebuilds data pointers.
- `open_fstab()`, `close_fstab()`, and `close_all_fstab()` manage locked, mmap-backed fstab files.

Important dependencies:
- Uses invutil path helpers such as `GetFstabFullPath()` and `GetNameOfInvIndex()`.
- Calls `invidx_commit()` for child inventory-index entries.

Notable observations:
- Mmap growth uses `lseek()` plus a one-byte write because Linux mappings do not autogrow.
- Closing truncates unused capacity and unlinks empty fstab files.
- Imported fstab entries commit their child index/storage-object data before adding the fstab row.
