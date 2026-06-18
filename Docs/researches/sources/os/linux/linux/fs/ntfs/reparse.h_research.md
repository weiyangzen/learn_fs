# File Research: sources/os/linux/linux/fs/ntfs/reparse.h

Header for reparse point support.

Exports:
- `reparse_index_name`.
- `ntfs_make_symlink()`.
- `ntfs_reparse_tag_dt_types()`.
- `ntfs_reparse_set_wsl_symlink()`.
- `ntfs_reparse_set_wsl_not_symlink()`.
- `ntfs_delete_reparse_index()`.
- `ntfs_remove_ntfs_reparse_data()` declaration.

Notable:
- `ntfs_remove_ntfs_reparse_data()` is declared here but not implemented in the grouped `reparse.c`.
