# File Research: sources/os/linux/linux-stable/fs/ntfs/reparse.c

`reparse.c` implements NTFS reparse point validation, WSL symlink/special-file representation, and `$Extend/$Reparse` index maintenance.

Key structures:
- `wsl_link_reparse_data` stores LX symlink type and target bytes.
- `reparse_index` models `$Extend/$Reparse` index entries.
- `reparse_index_name` is the Unicode `$R` index name.

Key functions:
- `ntfs_is_valid_reparse_buffer()` validates header size, nonzero tag, Microsoft vs non-Microsoft header length rules, and exact buffer size.
- `valid_reparse_data()` adds tag-specific validation for WSL symlinks and WSL special file tags.
- `ntfs_reparse_tag_mode()` maps known tags to Unix file modes.
- `ntfs_make_symlink()` reads `AT_REPARSE_POINT`, validates it, extracts WSL LX symlink targets into `ni->target`, and returns the file type mode.
- `ntfs_reparse_tag_dt_types()` loads an inode by MFT reference and maps its reparse tag to a directory-entry `DT_*` type.
- `set_reparse_index()` builds and inserts a `$R` index entry keyed by reparse tag and file reference.
- `remove_reparse_index()` reads the existing reparse tag from the attribute inode and removes the matching `$R` entry.
- `open_reparse_index()` opens `$Extend/$Reparse` and returns an index context for `$R`.
- `update_reparse_data()` removes the old index entry, overwrites the reparse point attribute, and inserts the new index entry.
- `ntfs_delete_reparse_index()` removes a reparse index entry and clears `FILE_ATTR_REPARSE_POINT` on the inode.
- `ntfs_set_ntfs_reparse_data()` validates input, creates `AT_REPARSE_POINT` if absent, updates the attribute/index, and marks filename/MFT state dirty.
- `ntfs_reparse_set_wsl_symlink()` creates an `IO_REPARSE_TAG_LX_SYMLINK` payload from a Unicode target converted to the current NLS encoding.
- `ntfs_reparse_set_wsl_not_symlink()` creates empty reparse payloads for WSL socket, FIFO, character-device, or block-device tags.

Dependencies:
- Attribute access through `ntfs_attr_readall()`, `ntfs_attr_add()`, `ntfs_attr_iget()`, `ntfs_inode_attr_pread()`, and `ntfs_inode_attr_pwrite()`.
- Index maintenance through index context helpers.
- MFT dirtying through `mark_mft_record_dirty()`.

Behavioral role:
- Used by `namei.c` to create WSL-compatible symlinks and special files.
- Used during unlink/delete to remove stale `$Reparse` index entries.
