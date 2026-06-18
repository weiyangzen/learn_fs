# File Research: sources/os/linux/linux-stable/fs/ntfs/reparse.h

`reparse.h` declares the NTFS reparse point API.

Contents:
- Declares external Unicode index name `reparse_index_name`.
- Declares helpers for interpreting and setting reparse data:
  - `ntfs_make_symlink()`
  - `ntfs_reparse_tag_dt_types()`
  - `ntfs_reparse_set_wsl_symlink()`
  - `ntfs_reparse_set_wsl_not_symlink()`
  - `ntfs_delete_reparse_index()`
  - `ntfs_remove_ntfs_reparse_data()`

Design role:
- Exposes reparse-point handling to inode/namespace code while hiding `$Extend/$Reparse` index internals.
- Note: this header declares `ntfs_remove_ntfs_reparse_data()`, but that implementation is not present in the read `reparse.c` file.
