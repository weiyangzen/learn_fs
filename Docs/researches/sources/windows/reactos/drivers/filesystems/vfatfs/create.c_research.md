# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/create.c

This file implements VFAT file creation/opening, 8.3 name conversion, directory lookup, volume opens, target-directory opens, create disposition handling, overwrite/supersede behavior, paging-file rules, share checks, and notifications.

Key functions:
- `vfat8Dot3ToString`
  - Converts an on-disk FAT 8.3 short name into a Unicode string.
  - Handles deleted-entry first-byte remapping from `0x05` to `0xe5`.
  - Applies base/ext lowercase flags and inserts the dot for non-volume entries with extensions.
- `FindFile`
  - Searches a directory for a file name or wildcard.
  - Builds a full path and first checks the in-memory FCB table for non-wildcard names.
  - Uppercases the search expression for `FsRtlIsNameInExpression`.
  - Iterates directory entries with `VfatGetNextDirEntry`, skips volume entries, detects corrupt missing names, compares long and short names, and optionally refreshes directory-entry data from an existing FCB.
  - Frees pinned directory pages and allocated strings on exit.
- `VfatOpenFile`
  - Resolves related-file parent state.
  - Checks removable-media verify with `IOCTL_DISK_CHECK_VERIFY`.
  - Gets or creates the FCB for the requested path.
  - Rejects invalid overwrite/delete cases, including existing directories, delete-pending FCBs, read-only overwrite/delete-on-close, root, and dot/dotdot.
  - Cancels delayed close if the FCB was queued for delayed release, including removal from the global close list and reference/context cleanup.
  - Attaches the FCB to the file object.
- `VfatCreateFile`
  - Unpacks create disposition/options, paging-file and open-target-directory flags.
  - Rejects unsupported file-id opens and invalid option combinations.
  - Denies opens when the volume is locked.
  - Handles volume opens, enforcing allowed dispositions/options, share access, FCB attachment, and open-handle counts.
  - Validates path syntax for illegal characters, illegal dot-only path components, double backslashes, absolute names with related file objects, target-root directory opens, and trailing backslashes.
  - Implements `SL_OPEN_TARGET_DIRECTORY` by resolving the target then opening/attaching the parent directory and trimming file-object name state.
  - On not-found paths, creates files/directories for `FILE_CREATE`, `FILE_OPEN_IF`, `FILE_OVERWRITE_IF`, or `FILE_SUPERSEDE` using `VfatAddEntry`, sets allocation size and extended attributes, and marks paging files.
  - On existing files, enforces `FILE_CREATE` collision, directory/non-directory option constraints, trailing-backslash rules, mapped-image write/delete checks, paging-file rules, hidden/system overwrite constraints, supersede/overwrite attributes and timestamps, allocation-size updates, and final information status.
  - Updates share access, delete-on-close CCB flag, directory-change notifications, open-handle counts, and create statistics.
- `VfatCreate`
  - Returns success for opens on the filesystem control device.
  - Acquires the volume directory resource, calls `VfatCreateFile`, releases the resource, and sets priority boost on success.

Notable design points:
- Create/open is serialized under `DeviceExt->DirResource`.
- The function supports both long and short names and checks both during directory searches.
- Delayed-close reuse is handled during open to avoid discarding an FCB that is immediately needed again.
- Delete-on-close is stored in the CCB during create and consumed later by cleanup.
- Existing file overwrite/supersede updates FAT timestamps and attributes before resizing allocation.
