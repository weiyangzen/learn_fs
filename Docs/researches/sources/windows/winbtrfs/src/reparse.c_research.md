# File Research: sources/windows/winbtrfs/src/reparse.c

## Purpose

`reparse.c` implements WinBtrfs reparse point operations: reading reparse data, setting reparse points, converting certain reparse points into native Btrfs symlinks, storing other reparse payloads, and deleting reparse points.

It bridges Windows reparse semantics with Btrfs inode types, file data, and extended attributes.

## Reparse Buffer Handling

The file defines `REPARSE_DATA_BUFFER_LX_SYMLINK`, a small structure used for Linux subsystem symlink reparse data. It also imports `fFsRtlValidateReparsePointBuffer` for system validation of incoming buffers.

## Getting Reparse Points

`get_reparse_point` takes a file object, caller buffer, buffer length, and returned length pointer. It acquires the tree lock shared and the FCB resource shared.

Behavior by file type/state:

- Native Btrfs symlink:
  - For LXSS callers (`ccb->lxss`), returns an `IO_REPARSE_TAG_LX_SYMLINK` buffer with a fixed integer payload.
  - Otherwise reads symlink target bytes from file data, converts UTF-8 to UTF-16, converts `/` to `\`, and returns an `IO_REPARSE_TAG_SYMLINK` buffer using relative symlink flags. Substitute and print names are identical.
- File with `FILE_ATTRIBUTE_REPARSE_POINT`:
  - Reads the stored reparse buffer from file data through `read_file`.
- Directory with `FILE_ATTRIBUTE_REPARSE_POINT`:
  - Copies `fcb->reparse_xattr` into the caller buffer.
- Other cases return `STATUS_NOT_A_REPARSE_POINT`.

It supports partial result behavior by setting as much header information as the buffer can hold and returning `STATUS_BUFFER_OVERFLOW` when needed.

## Setting Native Symlinks

`set_symlink` handles `IO_REPARSE_TAG_SYMLINK` and `IO_REPARSE_TAG_LX_SYMLINK` when they should become Btrfs symlink inodes.

For Windows symlink tags, it validates minimum length and substitute name length, converts the substitute name from UTF-16 to UTF-8, and normalizes `\` to `/`.

For LX symlink tags, it treats the LX payload name bytes as the target.

It then:

- Changes `fcb->type` to `BTRFS_TYPE_SYMLINK`.
- Rewrites inode mode bits from regular-file to symlink.
- Updates inode generation to the current superblock generation.
- Updates directory cache type when present.
- Truncates existing file data.
- Writes the target path into file data with `write_file2`.
- Updates ctime/mtime unless the CCB indicates user-specified timestamps.
- Updates subvolume root ctransid/ctime.
- Marks inode and file reference dirty.

## Setting Reparse Points

`set_reparse_point2` is the core setter. It rejects existing symlink inodes, rejects nonempty directories, validates buffer length, and calls `fFsRtlValidateReparsePointBuffer`.

Special cases:

- Mount points must target directories.
- Relative Windows symlinks on files and LX symlinks on files become native Btrfs symlinks through `set_symlink`.
- Directory, char device, and block device reparse data is stored in `fcb->reparse_xattr`.
- Other file reparse data is stored as file data after truncating the file.

After storing non-symlink reparse data, it sets `FILE_ATTRIBUTE_REPARSE_POINT`, marks attributes changed, updates timestamps and inode generation, updates subvolume root metadata, and marks the FCB dirty.

There are explicit FIXME notes for rejecting existing `FILE_ATTRIBUTE_REPARSE_POINT` and validating file/directory type more strictly.

`set_reparse_point` is the IRP-facing wrapper. It validates `FileObject`, rejects unexpected `Irp->UserBuffer`, checks `ccb`, checks caller write privileges, resolves ADS operations to the parent file, acquires tree shared and FCB exclusive resources, initializes rollback, calls `set_reparse_point2`, queues file-change notification on success, and either clears or applies rollback before releasing locks.

## Deleting Reparse Points

`delete_reparse_point` validates `FileObject`, `fcb`, `ccb`, caller privileges, and `fileref`, then acquires tree shared and FCB exclusive locks. It rejects too-short buffers, nonzero `ReparseDataLength`, and ADS deletion.

Behavior by file type:

- Native symlink:
  - Requires `IO_REPARSE_TAG_SYMLINK`.
  - Converts the inode back to regular file type/mode.
  - Clears `FILE_ATTRIBUTE_REPARSE_POINT`.
  - Updates timestamps, generation, sequence, directory cache type, subvolume root metadata, and dirty flags.
- File:
  - Truncates file data to zero.
  - Clears `FILE_ATTRIBUTE_REPARSE_POINT`.
  - Updates timestamps, inode metadata, and dirty flags.
- Directory:
  - Clears `FILE_ATTRIBUTE_REPARSE_POINT`.
  - Frees `fcb->reparse_xattr.Buffer`.
  - Marks reparse xattr changed.
  - Updates timestamps, inode metadata, and dirty flags.
- Unsupported file types return `STATUS_INVALID_PARAMETER`.

On success it queues a last-write/attributes notification. Rollback is cleared on success and applied on failure.

There are FIXME notes asking whether delete should verify the requested tag matches the stored reparse tag for file and directory reparse points.

## Dependencies and Shared State

This file depends on FCB/CCB/file-ref structures, tree locks, rollback helpers, file truncation and write helpers, UTF conversion helpers, timestamp conversion, dirty marking, and notification queuing. It calls `read_file` from `read.c` to materialize symlink targets and file-stored reparse payloads.

## Error Handling and Notes

The implementation carefully updates Btrfs inode state and Windows file attributes together. It uses rollback for mutating set/delete paths, but symlink conversion is broad: it changes inode type, mode, data, timestamps, directory-cache type, and root metadata in one operation. Reparse payload storage differs by type: native symlinks use file data as a target path, directories/devices use xattr storage, and generic file reparse points use file data.
