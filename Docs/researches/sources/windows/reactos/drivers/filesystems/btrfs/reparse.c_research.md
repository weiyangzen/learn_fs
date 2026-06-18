# File Research: sources/windows/reactos/drivers/filesystems/btrfs/reparse.c

## Purpose

`reparse.c` implements reparse point support for WinBtrfs, especially translation between Btrfs symlinks and Windows reparse buffers. It supports querying, setting, and deleting reparse points for symlinks, files, directories, and certain special file types.

## Main Responsibilities

- Return Windows reparse buffers for Btrfs symlinks.
- Support LX symlink behavior for LXSS-style callers.
- Convert Btrfs symlink target data between UTF-8 with `/` separators and Windows UTF-16 with `\` separators.
- Store non-symlink reparse data either as file data or directory/special-file xattrs.
- Convert regular files into symlinks for relative Windows symlink tags or LX symlink tags.
- Delete reparse points and restore symlink files to regular files.
- Update inode metadata, timestamps, attributes, subvolume root metadata, and dirty flags.
- Use rollback lists for mutating operations.

## Key Functions

- `get_reparse_point`: handles FSCTL-style reparse point retrieval.
- `set_symlink`: converts a supplied Windows or LX symlink reparse buffer into Btrfs symlink file contents and updates inode type/mode.
- `set_reparse_point2`: validates and applies a reparse point to an FCB.
- `set_reparse_point`: IRP wrapper for setting reparse data, including access checks, ADS handling, resource locking, rollback, and notifications.
- `delete_reparse_point`: removes reparse data or converts symlinks back to regular files, with metadata updates and rollback.

## Query Behavior

For `BTRFS_TYPE_SYMLINK`:

- If the CCB is marked `lxss`, it returns an `IO_REPARSE_TAG_LX_SYMLINK` buffer with a small generic payload.
- Otherwise, it reads the symlink target using `read_file`, converts UTF-8 to UTF-16, replaces `/` with `\`, duplicates the target as both substitute and print name, and marks the symlink as relative.

For files with `FILE_ATTRIBUTE_REPARSE_POINT`:

- Regular files read reparse bytes from file data using `read_file`.
- Directories return `fcb->reparse_xattr`.
- Other types return `STATUS_NOT_A_REPARSE_POINT`.

The function holds both `tree_lock` and the FCB resource shared while querying.

## Set Behavior

`set_reparse_point2` rejects attempts to set a reparse point on an existing Btrfs symlink and rejects non-empty directories. It validates the buffer via `fFsRtlValidateReparsePointBuffer`.

Special cases:

- Mount-point tags require a directory.
- A regular file with a relative `IO_REPARSE_TAG_SYMLINK`, or an `IO_REPARSE_TAG_LX_SYMLINK`, is converted into a Btrfs symlink using `set_symlink`.
- Directories, character devices, and block devices store reparse data in `fcb->reparse_xattr`.
- Other file types store the raw reparse buffer as file data after truncating the file.

`set_symlink` truncates existing file data, writes the symlink target bytes, changes inode mode to `__S_IFLNK`, updates generation/transid/sequence/timestamps, marks FCB and fileref dirty, and updates directory cache type if present.

## Delete Behavior

`delete_reparse_point` validates the request buffer, requires zero `ReparseDataLength`, rejects ADS targets, and then branches by file type:

- Symlinks require `IO_REPARSE_TAG_SYMLINK`, then are converted back to regular files by updating type and mode and clearing `FILE_ATTRIBUTE_REPARSE_POINT`.
- Regular files are truncated to zero and have the reparse attribute cleared.
- Directories clear `FILE_ATTRIBUTE_REPARSE_POINT`, free `reparse_xattr`, and mark the xattr changed.
- Unsupported types return `STATUS_INVALID_PARAMETER`.

All successful mutations update inode transaction metadata, sequence, timestamps unless user-set timestamps suppress them, and subvolume root change metadata. They also queue last-write/attribute notifications.

## Locking and Rollback

Set and delete wrappers acquire:

- `fcb->Vcb->tree_lock` shared
- `fcb->Header.Resource` exclusive

They initialize a rollback list, clear it on success, and call `do_rollback` on failure. This keeps truncate/write mutations recoverable if a later step fails.

## Notable Risks and Implementation Notes

- `set_reparse_point2` has FIXME comments for rejecting preexisting reparse attributes and validating allowed file/directory targets more strictly.
- Deletion has FIXME comments about checking that supplied reparse tags match stored tags for non-symlink file and directory cases.
- `set_symlink` only converts Windows symbolic links when `SYMLINK_FLAG_RELATIVE` is set; absolute Windows symlink behavior is not treated as a Btrfs symlink conversion here.
- LX symlink handling stores raw bytes after a small unknown header, matching the local `REPARSE_DATA_BUFFER_LX_SYMLINK` structure.
- Querying normal symlinks always reports `SYMLINK_FLAG_RELATIVE`.
