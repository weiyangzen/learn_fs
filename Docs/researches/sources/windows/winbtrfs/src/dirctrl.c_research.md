# File Research: sources/windows/winbtrfs/src/dirctrl.c

## Scope

This file implements WinBtrfs `IRP_MJ_DIRECTORY_CONTROL`, including directory enumeration (`IRP_MN_QUERY_DIRECTORY`) and directory change notification (`IRP_MN_NOTIFY_CHANGE_DIRECTORY`). It formats cached `dir_child` entries into Windows directory information classes, supports wildcard and specific-name queries, exposes `.` and `..`, handles reparse tags and EA sizes, and registers notify IRPs with FSRTL.

## Entry Points And Major APIs

- `get_reparse_tag_fcb(fcb)`: extracts the reparse tag for symlinks, directory reparse xattrs, or file-backed reparse data.
- `get_reparse_tag(Vcb, subvol, inode, type, atts, lxss, Irp)`: computes the reparse tag for a directory entry, including LXSS special-file tags and on-demand FCB opening for normal files/directories.
- `get_ea_len(Vcb, subvol, inode, Irp)`: reads the `EA` xattr, validates the EA buffer, and returns the Windows EA size reported in directory entries.
- `query_dir_item(fcb, ccb, buf, len, Irp, de, r)`: formats one `dir_entry` into the requested `FILE_*_DIR_INFORMATION` structure.
- `next_dir_entry(fileref, offset, de, pdc)`: advances through `.` / `..` and the directory's index-ordered `dir_child` list.
- `query_directory(Irp)`: implements `IRP_MN_QUERY_DIRECTORY`, including access checks, query-string state, wildcard matching, buffer packing, and status translation.
- `notify_change_directory(Vcb, Irp)`: validates a directory notify request, materializes the watched path in the CCB, and queues the IRP with `FsRtlNotifyFilterChangeDirectory`.
- `drv_directory_control(DeviceObject, Irp)`: exported `IRP_MJ_DIRECTORY_CONTROL` dispatch routine.

For non-MSVC builds, the file defines local versions of `FILE_ID_EXTD_DIR_INFORMATION` and `FILE_ID_EXTD_BOTH_DIR_INFORMATION` plus their information-class constants.

## Core Control Flow

Directory enumeration starts in `drv_directory_control`, which verifies that the request targets a filesystem VCB, clears `IoStatus.Information`, and dispatches by minor function. For `IRP_MN_QUERY_DIRECTORY`, `query_directory` validates CCB/FCB/file-ref state, checks `FILE_LIST_DIRECTORY` for user-mode callers, rejects the dummy FCB as empty, logs query flags, and resets per-handle query state on `SL_RESTART_SCAN`.

The first query with a filename stores `ccb->query_string` and records whether it is a wildcard expression or a specific filename. Later calls reuse the saved query unless a restart is requested. Specific-name queries are single-shot; if repeated without restart they return `STATUS_NO_MORE_FILES`.

`query_directory` takes `Vcb->tree_lock` shared and the target directory's `dir_children_lock` shared. It obtains the first candidate through `next_dir_entry`, maps the caller buffer with `map_user_buffer`, optionally resolves a specific name using the directory hash buckets, or skips entries until a wildcard expression matches. It writes the first entry through `query_dir_item`, then packs additional entries until the buffer is exhausted, alignment requires stopping, `SL_RETURN_SINGLE_ENTRY` is set, or no more matching entries exist. `NextEntryOffset` is written into the previous item each time another item is successfully added.

`next_dir_entry` returns `.` and `..` for non-root directory file references, then walks the `dir_children_index` list by Btrfs directory index. It hides the synthetic `$Root` child when not enumerating the apparent root, preventing recursive exposure below normal subdirectories.

`query_dir_item` resolves enough metadata for the requested information class. For normal entries it may use an already attached child fileref/FCB, or it may look up the inode item and derive attributes/EA lengths directly. For subvolume entries (`TYPE_ROOT_ITEM`), it finds the corresponding root, validates the parent relationship unless the entry is synthetic `$Root`, and reports `SUBVOL_ROOT_INODE`. For `.` and `..`, it uses the current or parent FCB. It then fills the requested structure, including timestamps, sizes, allocation size, attributes, EA size or reparse tag, file IDs, and filename bytes.

Change notification is handled in `notify_change_directory`. It validates CCB and fileref state, checks list-directory access, takes tree and FCB resources, ensures the target is a directory, computes and caches the full watched filename in the CCB if needed, then calls `FsRtlNotifyFilterChangeDirectory`. Pending notification IRPs are not completed by this dispatch path.

## Supported Directory Information Classes

- `FileBothDirectoryInformation`
- `FileDirectoryInformation`
- `FileFullDirectoryInformation`
- `FileIdBothDirectoryInformation`
- `FileIdFullDirectoryInformation`
- `FileIdExtdDirectoryInformation`
- `FileIdExtdBothDirectoryInformation`
- `FileNamesInformation`

The "both" classes do not provide short names; short-name length is set to zero. Extended ID classes include a 128-bit file ID. File ID full/both classes use `make_file_id` when a real root is known and fall back to the dummy FCB identity otherwise.

## Important State Mutated

- `ccb->query_dir_offset` tracks the next directory index to enumerate.
- `ccb->query_string`, `has_wildcard`, and `specific_file` persist enumeration filters across calls.
- `ccb->filename` is allocated and cached for directory notification watches.
- `Irp->IoStatus.Information` is set to the number of bytes written for query-directory calls.
- Pending notify IRPs are inserted into `Vcb->DirNotifyList` under `Vcb->NotifySync` by FSRTL.

## Dependencies

Windows/IFS dependencies include `FsRtlDoesNameContainWildCards`, `FsRtlIsNameInExpression`, `FsRtlNotifyFilterChangeDirectory`, `IoCheckEaBufferValidity`, `RtlUpcaseUnicodeString`, resource locking, file information structures, reparse tags, and IRP completion conventions.

Project-local dependencies include `open_fcb`, `free_fcb`, `find_item`, `find_next_item`, `get_xattr`, `read_file`, `get_file_attributes`, `make_file_id`, `fileref_get_filename`, `map_user_buffer`, Unicode/Unix time conversion helpers, `sector_align`, and Btrfs metadata types (`INODE_ITEM`, `DIR_ITEM`, `TYPE_ROOT_ITEM`, `TYPE_INODE_ITEM`, `TYPE_DIR_INDEX`).

## Notable Behaviors

- Symlinks report end-of-file and allocation size as zero in directory listings, matching Windows reparse-point presentation rather than the stored Btrfs symlink target length.
- Sparse files report `st_blocks` as allocation size; other files report sector-aligned logical size.
- For `FileBothDirectoryInformation` and `FileFullDirectoryInformation`, the `EaSize` field is overloaded with the reparse tag when the entry has `FILE_ATTRIBUTE_REPARSE_POINT`, following Windows directory-query conventions.
- LXSS special file types map to Linux subsystem reparse tags (`IO_REPARSE_TAG_AF_UNIX`, `IO_REPARSE_TAG_LX_FIFO`, `IO_REPARSE_TAG_LX_CHR`, `IO_REPARSE_TAG_LX_BLK`) when `ccb->lxss` is true.
- Initial enumeration returning no match is translated from `STATUS_NO_MORE_FILES` to `STATUS_NO_SUCH_FILE`, matching Windows query-directory behavior.
- Multiple-entry packing aligns remaining buffer length to 8 bytes for most directory info classes and to 4 bytes for `FileNamesInformation`.

## Risks And Edge Cases

- In `FileIdExtdDirectoryInformation` and `FileIdExtdBothDirectoryInformation`, the 128-bit `FileId` is filled from the containing directory `fcb->inode` and `fcb->subvol->id`, not from the entry's resolved `inode` and `r`; this appears to report the directory's ID for every entry.
- The extended ID classes call `get_reparse_tag(fcb->Vcb, r, inode, ...)` unconditionally. If `r` is NULL for a dummy/inaccessible entry, `get_reparse_tag` can still call `open_fcb` for file/directory reparse attributes, which expects a valid root.
- `get_reparse_tag_fcb` reads four bytes from a file-backed reparse point but does not verify that `read_file` actually returned four bytes in `br`.
- `get_ea_len` returns zero for invalid EA buffers after logging a warning, so corrupted EA xattrs are hidden from directory listings rather than failing enumeration.
- `query_directory` advances `ccb->query_dir_offset` after obtaining the first candidate before the caller buffer is mapped and before `query_dir_item` succeeds. Buffer-mapping failures or first-entry buffer overflow can therefore consume an entry from the handle's enumeration state.
- Specific-file lookup for case-insensitive mode relies on upcased hash buckets and full uppercase comparison. Correctness depends on the directory cache's `name_uc` state being complete and in sync.
- `notify_change_directory` allocates `ccb->filename.Buffer`; if the second `fileref_get_filename` fails, the buffer remains attached to the CCB for later cleanup elsewhere.

## Summary

`dirctrl.c` is the directory enumeration and notification layer for WinBtrfs. It turns cached Btrfs directory children and inode metadata into Windows query-directory records, maintains per-handle enumeration filters and offsets, reports reparse/EA/file-id metadata, and registers directory change watches through FSRTL.
