# File Research: sources/local-fs/ntfs-3g/libntfs-3g/ea.c

## Role

Handles NTFS extended attributes (`AT_EA` and `AT_EA_INFORMATION`) and WSL-specific EA records such as `$LXMOD` and `$LXDEV`.

## Main Functions

- `ntfs_need_ea()` ensures an EA-related attribute exists, respecting `XATTR_REPLACE` and requiring NTFS major version at least 3.
- `restore_ea_info()` restores or removes `EA_INFORMATION` after a failed EA update while preserving the original `errno`.
- `ntfs_update_ea()` writes `EA_INFORMATION` first, then writes/truncates `AT_EA`, restoring old info on failure when available.
- `ntfs_get_ntfs_ea()` returns the raw `AT_EA` attribute or the needed size.
- `ntfs_set_ntfs_ea()` validates packed EA entries, computes `EA_INFORMATION`, creates missing attributes, and updates both EA structures.
- `ntfs_remove_ntfs_ea()` removes both `AT_EA` and `AT_EA_INFORMATION`, trying to restore info if the second step fails.
- `ntfs_ea_check_wsldev()` scans EA records for `$LXDEV` and returns a `dev_t`.
- `ntfs_ea_set_wsl_not_symlink()` writes WSL mode/device EA records for non-symlink special files.

## Dependencies

Uses NTFS attribute, directory/index, layout, xattr, and logging helpers. Uses platform `major()`, `minor()`, and `makedev()` macros through conditional system headers.

## Important Behavior

`ntfs_set_ntfs_ea()` requires every EA entry to have a nonzero `next_entry_offset`, 4-byte alignment, a nonempty NUL-terminated name, and value bounds that fit within the entry. It does not validate EA name characters because Windows `chkdsk` accepts broad names.

For WSL, `$LXMOD` is always written and `$LXDEV` is added only for character or block devices.

## Research Notes

This file is used both for user-visible NTFS EA xattrs and as support for WSL special files created by `dir.c`. It updates inode dirty flags and filename dirty flags because EA presence affects metadata visible in filename attributes.
