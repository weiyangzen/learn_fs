# File Research: sources/windows/reactos/drivers/filesystems/btrfs/dirctrl.c

Implements directory control for the Btrfs filesystem driver: query-directory enumeration, exact/wildcard name filtering, directory information class formatting, EA/reparse tag reporting, `.`/`..` synthesis, hidden `$Root` handling, and change-notification registration.

Key entry points:
- `drv_directory_control()` dispatches `IRP_MJ_DIRECTORY_CONTROL`, rejects volume/non-filesystem device objects, and routes `IRP_MN_QUERY_DIRECTORY` to `query_directory()` and `IRP_MN_NOTIFY_CHANGE_DIRECTORY` to `notify_change_directory()`.
- `query_directory()` validates FCB/CCB/fileref state and access, processes query flags, stores/reuses query patterns in the CCB, locks the VCB tree and directory child list, locates matching entries, fills one or more records, advances `query_dir_offset`, and returns byte count in `IoStatus.Information`.
- `query_dir_item()` converts one internal `dir_entry` into the requested Windows directory information structure.
- `next_dir_entry()` walks the in-memory `dir_children_index`, synthesizing `.` and `..` for non-root directory opens and hiding the synthetic `$Root` entry except at the apparent root.
- `notify_change_directory()` validates access and directory type, computes the watched path name if needed, and registers the IRP with `FsRtlNotifyFilterChangeDirectory()`.

Directory information support:
- Supports `FileBothDirectoryInformation`, `FileDirectoryInformation`, `FileFullDirectoryInformation`, `FileIdBothDirectoryInformation`, `FileIdFullDirectoryInformation`, `FileNamesInformation`, and Vista-style `FileIdExtdDirectoryInformation` / `FileIdExtdBothDirectoryInformation`.
- Populates timestamps from Btrfs `INODE_ITEM` fields, translating Unix/Btrfs time to Windows time.
- Reports `EndOfFile` as zero for symlinks and `st_size` otherwise.
- Reports allocation size as zero for symlinks, `st_blocks` for sparse files, or sector-aligned logical size otherwise.
- Reports file attributes from cached FCBs when available or by calling `get_file_attributes()` from inode metadata.
- Reports EA size from cached/fetched EA xattrs, but substitutes reparse tags for information classes whose `EaSize` field doubles as reparse tag reporting.
- Reports short-name lengths as zero because Btrfs has no DOS 8.3 short-name namespace.

Reparse and EA helpers:
- `get_reparse_tag_fcb()` returns symlink tags directly, extracts directory reparse tags from the reparse xattr, or reads a file-backed reparse buffer tag from file contents.
- `get_reparse_tag()` maps Btrfs symlinks and LXSS socket/FIFO/char/block device types to Windows reparse tags; for normal files/directories it opens the target FCB when the reparse attribute is present.
- `get_ea_len()` fetches the Btrfs EA xattr, validates it with `IoCheckEaBufferValidity()`, and computes the packed Windows EA length.

Filtering and enumeration:
- Query patterns are stored on the CCB. `SL_RESTART_SCAN` clears stored state and resets offset.
- A single `*` or absent filename means full enumeration; non-wildcard names become exact lookups; wildcard names are upcased for case-insensitive `FsRtlIsNameInExpression()`.
- Exact lookup uses the directory child hash tables, choosing case-sensitive or upcased hash buckets based on `ccb->case_sensitive`.
- Multi-entry output aligns each next record to 8 bytes for most directory classes and 4 bytes for `FileNamesInformation`.
- `SL_RETURN_SINGLE_ENTRY` and exact-file queries stop after the first successful entry.

Locking and state:
- Directory enumeration holds `Vcb->tree_lock` shared and the directory FCB’s `dir_children_lock` shared while reading child lists and formatting returned records.
- Change notification holds `tree_lock` shared and the target FCB resource exclusive while validating/registering the watch.
- Query state persists in `ccb->query_dir_offset`, `ccb->query_string`, `ccb->has_wildcard`, and `ccb->specific_file`.

Filesystem relevance:
- This file is the Windows directory enumeration facade over Btrfs directory index metadata cached by `create.c`. It is responsible for making Btrfs inode/subvolume/xattr/reparse state look like standard Windows directory query records.

Notable risks:
- In the extended file ID information cases, `FileId.Identifier` is filled from the queried directory FCB (`fcb->inode`, `fcb->subvol->id`) rather than the child entry’s `inode`/`r`; this looks wrong for directory listings where each returned row should identify the listed child.
- `query_dir_item()` may open child FCBs and read reparse/file data while enumeration locks are held; this is functional but increases deadlock and latency sensitivity.
- `get_reparse_tag()` opens an FCB to inspect reparse data for listed entries, so malformed or expensive reparse metadata can affect ordinary directory listings.
- The exact-match path allocates an upcased string for case-insensitive matching and frees it correctly, but the surrounding enumeration state is updated before exact lookup, making restart/specific-file behavior worth regression testing.
