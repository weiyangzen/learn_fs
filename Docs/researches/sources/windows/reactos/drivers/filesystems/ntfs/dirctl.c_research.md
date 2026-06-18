# File Research: sources/windows/reactos/drivers/filesystems/ntfs/dirctl.c

Read status: complete file, 622 lines.

This file implements directory enumeration for `IRP_MJ_DIRECTORY_CONTROL`.

Key entry points:
- `NtfsGetFileSize()` finds a `$DATA` stream and returns data and allocated lengths.
- `NtfsGetNamesInformation()`, `NtfsGetDirectoryInformation()`, `NtfsGetFullDirectoryInformation()`, and `NtfsGetBothDirectoryInformation()` format one directory entry into the requested Windows information class.
- `NtfsQueryDirectory()` manages search patterns in the CCB, scan restart/index flags, buffer filling, duplicate short/long-name suppression, and repeated calls to `NtfsFindFileAt()`.
- `NtfsDirectoryControl()` dispatches minor functions. Query directory is implemented; notify-change directory returns `STATUS_NOT_IMPLEMENTED`.

Important dependencies:
- Directory lookup/index traversal: `NtfsFindFileAt`.
- File-record attribute extraction: `GetBestFileNameFromRecord`, `GetFileNameFromRecord`, `GetStandardInformationFromRecord`.
- User-buffer mapping: `NtfsGetUserBuffer`.
- Per-open search state in `NTFS_CCB`.

Notable behavior and risks:
- Compressed directories are rejected with `STATUS_NOT_IMPLEMENTED`.
- Duplicate suppression only ignores immediately adjacent entries with the same MFT record.
- The per-entry helpers support partial first-entry copy semantics and return overflow when the caller buffer cannot hold a complete record.
- `NtfsQueryDirectory()` sets `Irp->IoStatus.Information`, but `NtfsDirectoryControl()` later unconditionally resets `IrpContext->Irp->IoStatus.Information = 0`, which can erase the byte count from successful queries.
