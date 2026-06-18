# File Research: sources/local-fs/ntfs-3g/libntfs-3g/reparse.c

## Purpose
Handles NTFS reparse points, including junctions, Windows symlinks, WSL symlinks/special files, raw reparse xattrs, and `$Extend/$Reparse:$R` index maintenance.

## Main Interfaces
- `ntfs_make_symlink()` converts supported reparse point data into a Linux symlink target.
- `ntfs_possible_symlink()` checks whether reparse data might describe a link.
- `ntfs_get_ntfs_reparse_data()`, `ntfs_set_ntfs_reparse_data()`, `ntfs_remove_ntfs_reparse_data()` expose raw reparse data through xattr-style APIs.
- `ntfs_delete_reparse_index()` removes the reparse index entry.
- `ntfs_reparse_check_wsl()` validates WSL special file tags.
- `ntfs_reparse_set_wsl_symlink()` and `ntfs_reparse_set_wsl_not_symlink()` create WSL reparse data.
- `ntfs_get_reparse_point()` returns validated reparse data.

## Control Flow
Validation checks reparse header sizing, Microsoft vs non-Microsoft header length rules, tag-specific payload bounds, directory requirement for mount points, WSL symlink type, and WSL special-file flags. Link conversion distinguishes junction/full paths (`\??\`, `\\?\Volume{}`), absolute paths (`\` or `X:\`), relative paths, and WSL symlinks. Same-volume targets are resolved through directory indexes with case correction; unresolved drive/volume targets are mapped through `/.NTFS-3G/` stubs.

Setting raw reparse data validates the payload, opens `$Extend/$Reparse`, creates the unnamed `$REPARSE_POINT` attribute if needed, sets `FILE_ATTR_REPARSE_POINT`, writes the data, and inserts/updates the index entry. Removal removes the index first, removes the attribute, clears the file attribute flag, and marks filename index data dirty.

## Integration Points
Depends on inode, directory, index, attribute, volume, xattr, and EA helpers. It opens `$Extend/$Reparse`, uses `$R` index entries keyed by reparse tag plus file ID, and coordinates with filename sync through `NInoFileNameSetDirty()` when reparse flags/tags change.

## Risks and Invariants
- Link target resolution intentionally stops before dereferencing nested reparse points.
- Relative symlink resolution has a hard safety limit of 32 path components.
- Several structures use packed on-disk data and comments warn about alignment-sensitive processors.
- Raw set warns that EA compatibility is no longer checked because Windows 10 requires otherwise, which may affect older Windows versions.
- Failed index restore/removal paths can leave inconsistency and are logged as possible corruption.
