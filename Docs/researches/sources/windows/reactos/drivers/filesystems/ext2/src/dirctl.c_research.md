# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/dirctl.c

This file implements directory-control IRPs for Ext2Fsd. It converts ext2/ext3 directory entries into Windows directory-information records, supports wildcard query state, handles htree-indexed directories when enabled, registers change-notification IRPs, reports directory changes, and checks directory emptiness.

Key responsibilities:
- Serve `IRP_MN_QUERY_DIRECTORY` and `IRP_MN_NOTIFY_CHANGE_DIRECTORY`.
- Populate all supported Windows directory information classes.
- Maintain per-handle search pattern and enumeration position in the CCB.
- Hide configured names and skip `.`/`..` during enumeration.
- Translate OEM ext directory names to Unicode and apply Windows wildcard matching.
- Bridge ext3 htree readdir callbacks into the Windows output buffer.

Important functions:
- `Ext2GetInfoLength`: Returns the fixed prefix length for each supported `FILE_INFORMATION_CLASS`.
- `Ext2ProcessEntry`: Builds `FILE_DIRECTORY_INFORMATION`, full, both, id-full, id-both, or names-only records; loads inode data if no MCB is cached; follows symlink MCBs; sets file attributes, sizes, times, file ids, and symlink reparse tags.
- `Ext2IsWearingCloak`: Applies per-volume hiding prefix/suffix filters while preserving `.` and `..`.
- `Ext2FillEntry`: Htree callback used by `ext3_dx_readdir`; converts names, filters them, runs search-pattern matching, and calls `Ext2ProcessEntry`.
- `Ext2QueryDirectory`: Validates the target directory, acquires the FCB resource, initializes/reuses the search pattern, manages restart/index/single-entry flags, tries indexed-directory enumeration, and falls back to linear ext directory scanning.
- `Ext2NotifyChangeDirectory`: Registers a notify IRP with `FsRtlNotifyFullChangeDirectory` and leaves it pending.
- `Ext2NotifyReportChange`: Emits change notifications for an MCB path through `FsRtlNotifyFullReportChange`.
- `Ext2DirectoryControl`: Minor-function dispatcher.
- `Ext2IsDirectoryEmpty`: Delegates to `ext3_is_dir_empty` for real directories and treats non-directories/symlinks as empty for this helper.

Important interactions:
- Calls into htree support through `ext3_dx_readdir` when `EXT2_HTREE_INDEX` and directory-index features are present.
- Uses `Ext2ReadInode` for linear directory entry headers and `Ext2ProcessEntry` for the final Windows record.
- Uses `Ext2SearchMcb`, `Ext2LookupFile`, and `Ext2FollowLink` to enrich directory results from cached namespace state.
- Directory change registration and reporting share `Vcb->NotifySync` and `Vcb->NotifyList`.

Notable behavior and risks:
- `Ext2QueryDirectory` directly zeros the caller output buffer before enumeration and writes the final previous `NextEntryOffset` to zero via `fc.efc_prev`.
- If htree enumeration returns `ERR_BAD_DX_DIR`, it clears `EXT3_INDEX_FL` in memory and scans linearly without marking the inode dirty.
- Linear scanning treats `rec_len == 0` as "skip to end of block", preventing an infinite loop but potentially masking malformed entries.
- Hidden-dot logic marks most names beginning with `.` as hidden, separate from the configured cloak filters.
