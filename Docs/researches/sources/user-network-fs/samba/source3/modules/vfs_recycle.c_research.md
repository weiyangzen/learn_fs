# sources/user-network-fs/samba/source3/modules/vfs_recycle.c

## Purpose
`vfs_recycle.c` implements a Samba recycle bin. Instead of deleting regular files, it moves them into a configured repository, optionally preserving directory structure, versioning duplicate names, and touching timestamps.

## Important APIs, Types, And Functions
- `struct recycle_config_data` stores repository, `keeptree`, `versions`, touch flags, exclude lists, version-exclusion list, directory modes, and size limits.
- `vfs_recycle_connect()` reads configuration, performs Samba substitutions in the repository path, and stores config as handle data.
- Helpers include `recycle_directory_exist`, `recycle_file_exist`, `recycle_get_file_size`, `recycle_create_dir`, `matchdirparam`, `matchparam`, and `recycle_do_touch`.
- `recycle_unlink_internal()` performs the recycle-or-purge decision and rename.
- `recycle_unlinkat()` bypasses directories and recycles regular unlink calls.

## Control Flow
Connect skips IPC/print shares, allocates config, expands `recycle:repository`, trims trailing slash, reads booleans/lists/modes/sizes, and stores the result. On file unlink, the module builds the full path, avoids recycling anything already inside the repository, enforces min/max file-size policy, splits parent/base, applies filename and directory exclude patterns, creates the target repository/tree, builds a destination `smb_filename`, handles existing destination by deleting or generating `Copy #N of ...`, then delegates `SMB_VFS_NEXT_RENAMEAT`. If setup or rename fails, it falls back to actual unlink. Touch options update atime/mtime using a synthetic pathref.

## State And Persistence
Configuration is per connection. Persistent state is the repository directory and moved files. Versioning state is implicit in existing destination filenames. The module does not maintain an index.

## Dependencies And Integration Points
It depends on Samba substitutions, VFS stat/mkdir/rename/unlink/fntimes hooks, wildcard matching, connection/session user data, and debug class registration. It integrates at `unlinkat_fn`, leaving directory removal untouched.

## Risks
- Recycling is implemented as rename; cross-filesystem repository paths can fail and cause purge fallback.
- Repository path prefix checks are string-based and can be sensitive to normalization.
- Size max logic applies to individual file size, not total recycle-bin usage; a FIXME notes this.
- Version loop can be expensive in directories with many duplicate copies.
- Failure paths often purge the file to preserve unlink semantics.

## Test Signals
- Delete files with default and custom repositories; verify rename target and optional tree preservation.
- Test `exclude`, `exclude_dir`, `noversions`, `versions`, `minsize`, and `maxsize`.
- Delete a file already in the recycle repository and verify it is purged.
- Test duplicate names and `Copy #N` generation.
- Verify touch/touch_mtime behavior after recycle.
