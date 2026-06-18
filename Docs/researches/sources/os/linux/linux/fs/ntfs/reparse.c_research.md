# File Research: sources/os/linux/linux/fs/ntfs/reparse.c

Handles NTFS reparse point validation, interpretation, creation, indexing, and deletion, with explicit support for WSL-style symlinks and special files.

Validation and interpretation:
- `ntfs_is_valid_reparse_buffer()` validates header size, nonzero tag, Microsoft vs non-Microsoft header sizing, and exact expected size.
- `valid_reparse_data()` adds tag-specific checks for WSL symlinks, AF_UNIX sockets, FIFO, char, and block devices.
- `ntfs_reparse_tag_mode()` maps reparse tags to Linux mode type bits.
- `ntfs_make_symlink()` reads `AT_REPARSE_POINT`, validates it, extracts WSL symlink target into `ni->target`, and returns the implied mode.
- `ntfs_reparse_tag_dt_types()` opens an inode by MFT reference, reads reparse data, and maps tags to directory-entry types.

Index handling:
- Global `reparse_index_name` is `$R`.
- `open_reparse_index()` opens `FILE_Extend`, looks up `$Reparse`, opens its inode, and gets the `$R` index context.
- `set_reparse_index()` builds and inserts a `$Reparse` index entry keyed by tag and file reference.
- `remove_reparse_index()` reads the old tag from the reparse attribute and removes the matching index entry.

Mutation:
- `update_reparse_data()` opens the `AT_REPARSE_POINT` attribute inode, removes any old index entry, overwrites reparse data, inserts the new index entry, and marks metadata dirty.
- `ntfs_delete_reparse_index()` removes the index entry and clears `FILE_ATTR_REPARSE_POINT` from inode flags/name metadata.
- `ntfs_set_ntfs_reparse_data()` creates the reparse attribute if needed, validates NTFS version, sets inode flags, updates data and index, and rolls back flags on failure.
- `ntfs_reparse_set_wsl_symlink()` converts target to NLS bytes, builds `IO_REPARSE_TAG_LX_SYMLINK` data, stores it, and keeps `ni->target` on success.
- `ntfs_reparse_set_wsl_not_symlink()` creates zero-length WSL special-file reparse data for socket/FIFO/char/block device tags.

Notable observation:
- `reparse.h` declares `ntfs_remove_ntfs_reparse_data()`, but this grouped `reparse.c` does not define it.

Important dependencies:
- Attribute read/write/add/remove APIs, index APIs, MFT dirtying, Unicode conversion, and NTFS layout tag definitions.
