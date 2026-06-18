# File Research: sources/windows/windows-driver-samples/filesys/fastfat/fileinfo.c

## Role

`fileinfo.c` implements FastFAT file information query and set handling for `IRP_MJ_QUERY_INFORMATION` and `IRP_MJ_SET_INFORMATION`. It is the central metadata mutation path for file size, allocation size, delete-on-close, rename, timestamps, attributes, current byte offset, valid data length, and returned name/standard/basic/network-open metadata.

## Entry Points

- `FatFsdQueryInformation`: FSD dispatch wrapper for query information. Enters the filesystem, establishes top-level IRP state, creates an IRP context, calls `FatCommonQueryInformation`, and funnels exceptions through `FatProcessException`.
- `FatFsdSetInformation`: Same pattern for set information, calling `FatCommonSetInformation`.

Both wrappers are pageable and ignore the `VolumeDeviceObject` parameter after dispatch setup.

## Query Flow

`FatCommonQueryInformation` decodes the `FILE_OBJECT` through `FatDecodeFileObject`, rejects `UserVolumeOpen`, and supports `UserFileOpen`, `UserDirectoryOpen`, and internal `DirectoryFile`.

Important synchronization:

- Acquires the VCB exclusive for `FileNameInformation`, `FileNormalizedNameInformation`, and `FileAllInformation` because full-name construction must be synchronized with deletion.
- Acquires the FCB shared except for paging files, with a removable-media exception for ReadyBoost-style paging-file opens.
- Verifies the FCB before reading metadata.

Supported classes:

- `FileAllInformation`
- `FileBasicInformation`
- `FileStandardInformation`
- `FileInternalInformation`
- `FileEaInformation`
- `FilePositionInformation`
- `FileNameInformation`
- `FileNormalizedNameInformation`
- `FileAlternateNameInformation`
- `FileNetworkOpenInformation`

Unsupported classes return `STATUS_INVALID_PARAMETER`.

Buffer accounting is done by decrementing a local `Length`. If it becomes negative, the final status is `STATUS_BUFFER_OVERFLOW`, length is forced to zero, and `IoStatus.Information` reports bytes actually filled.

## Query Helpers

- `FatQueryBasicInfo`: Returns creation, last access, last write, and FAT attributes. Root directories synthesize `1/1/1980` via local-to-system conversion. Temporary FCB state maps to `FILE_ATTRIBUTE_TEMPORARY`; empty attributes become `FILE_ATTRIBUTE_NORMAL`.
- `FatQueryStandardInfo`: Returns one hard link, delete-pending state, allocation size, EOF, and directory flag. It resolves lazy allocation-size hints with `FatLookupFileAllocationSize`.
- `FatQueryInternalInfo`: Uses `FatGenerateFileIdFromFcb`.
- `FatQueryEaInfo`: Zeroes EA size. The older EA-length lookup block is disabled with `#if 0`.
- `FatQueryPositionInfo`: Copies `FileObject->CurrentByteOffset`.
- `FatQueryNameInfo`: Builds full names, optionally normalized. If the open was by short name and the file has an LFN, it returns the path prefix plus converted short name so callers see the name context they opened. Handles overflow by setting `*Length = -1`.
- `FatQueryShortNameInfo`: Converts the FCB short OEM name to Unicode and returns it as alternate-name information.
- `FatQueryNetworkInfo`: Combines basic and standard-style metadata for network open information, including root timestamp synthesis and allocation lookup.

## Set Flow

`FatCommonSetInformation` decodes the object, rejects volume opens, performs oplock checks for allocation/EOF/VDL changes on normal files, rejects root DCB mutations, and acquires:

- VCB exclusive for disposition and rename, preventing concurrent creates.
- FCB exclusive for most set operations, except paging-file deadlock avoidance with removable-media exception.

It verifies the FCB and does rename/delete oplock checks where needed. Supported classes:

- `FileBasicInformation`
- `FileDispositionInformation`
- `FileRenameInformation`
- `FilePositionInformation`
- `FileAllocationInformation`
- `FileEndOfFileInformation`
- `FileValidDataLengthInformation`

`FileLinkInformation` returns `STATUS_INVALID_DEVICE_REQUEST`; other unsupported classes return `STATUS_INVALID_PARAMETER`.

## Metadata Mutation Helpers

`FatSetBasicInfo` updates timestamps and attributes in the dirent and FCB.

Key behavior:

- `-1` timestamp values mean "do not update"; corresponding CCB user-set flags are recorded.
- FAT timestamp conversion validates values and special-cases local `12/31/1979` into FAT `1/1/1980`.
- Creation time is rounded to FAT precision, last access is truncated to local-day granularity, and last write is rounded to two seconds.
- Only FAT-supported attributes are persisted.
- Directory attribute consistency is enforced.
- Temporary state is mirrored to `FCB_STATE_TEMPORARY` and `FO_TEMPORARY_FILE`.
- Parent directory oplocks are broken on Windows 8+ when relevant metadata changes.

`FatSetDispositionInfo` implements delete-on-close.

It rejects deletion of:

- Read-only files.
- User-mapped image files that cannot be flushed.
- Root directories.
- Non-empty directories.

It dirties media to detect write protection. Floppy media receives special FAT-area touch/write-through handling; other media dirty the target dirent BCB. On success it sets `FCB_STATE_DELETE_ON_CLOSE` and `FileObject->DeletePending`; for directories it notifies directory-change waiters. Clearing disposition removes those flags.

`FatSetPositionInfo` updates `CurrentByteOffset`, enforcing device alignment for non-buffered file objects.

## Rename Handling

`FatSetRenameInfo` is the largest and most complex routine in the file. It performs a two-phase rename:

Phase 1 validates legality and allocates/locates required metadata:

- Rejects root rename.
- For directory renames, walks child FCBs bottom-up, rejecting active children unless batch oplocks can be broken.
- Purges referenced file objects for directories.
- Determines target DCB and new name from either simple rename buffer or target directory file object.
- Handles same-name, case-only rename, and cross-directory rename detection.
- Converts candidate names to upcased OEM 8.3 form when possible.
- Looks up tunnel cache data for restored short/long names and creation time.
- Determines whether LFN dirents are required.
- In non-Chicago mode, requires valid 8.3 names and disables LFN/case magic.
- Checks for target collisions and replacement legality. Replacement rejects directories and read-only targets, and rejects targets with active opens or image sections unless oplock handling posts the IRP.
- Allocates new dirent space when moving directories or changing required dirent count.

Phase 2 mutates on-disk and in-memory structures:

- Sends removal or old-name rename notifications.
- Copies the source dirent, tunnels source metadata, and enters a state where abnormal failure may invalidate the FCB.
- Deletes source dirents if moving allocation.
- Deletes replacement targets with `FatDeleteFile`.
- Selects final short/LFN names, constructs new dirents, and handles LFN-plus-dirent page-boundary splits.
- Restores tunneled timestamps when applicable.
- Removes old names from prefix structures and frees cached full/exact-case names.
- Updates dirent offsets, parent DCB queue membership, and parent DCB pointer.
- Breaks parent directory oplocks on Windows 8+.
- For cross-directory directory moves, updates the `..` dirent cluster pointer.
- Reconstructs FCB short/long/full names and prefix entries.
- Marks file objects modified and suppresses automatic last-write update where appropriate.
- Emits final notifications as modified, added, or renamed-new-name depending on replacement/cross-directory status.
- Renames OS/2 EA owner metadata on non-FAT32 when needed.

Failure handling is intentionally non-transactional; after certain disk mutations, abnormal termination can only mark the FCB bad.

## Size, Allocation, and VDL

`FatSetAllocationInfo` changes file allocation size.

- Directories are rejected.
- Range validity is checked with `FatIsIoRangeValid`.
- Lazy allocation-size hints are resolved.
- If a data section exists without a shared cache map, it initializes caching to coordinate with Cache Manager.
- Expansions call `FatAddFileAllocation`.
- Shrinks may truncate file size, VDL, and valid-data-to-disk after `MmCanFileBeTruncated` and purge-failure checks.
- Paging I/O is synchronized while truncating.
- Cache sizes are updated with `CcSetFileSizes`.
- Dirent file size and notifications are updated after irreversible truncation.
- Abnormal termination can unwind in-memory sizes before the irreversible point.

`FatSetEndOfFileInfo` changes EOF.

- Only regular files are allowed.
- `AdvanceOnly` lazily advances the dirent file size without reducing it, used for lazy file-size writeback.
- Expands allocation when EOF exceeds allocation.
- Shrinks coordinate with purge failure mode, `MmCanFileBeTruncated`, and paging I/O.
- Updates FCB file size, VDL, valid-data-to-disk, cache sizes, dirent size, notifications, and truncate-on-close state.
- On abnormal termination it restores in-memory sizes and attempts no-raise dirent size rollback for suspend/removable-media failure cases.

`FatSetValidDataLengthInfo` explicitly changes VDL.

- Requires `CCB_FLAG_MANAGE_VOLUME_ACCESS`.
- Only files are allowed.
- VDL may only move forward and may not exceed file size.
- Rejects mapped files that cannot be purged.
- Flushes and purges existing cache before exposing new valid data.
- Updates `ValidDataLength`, `ValidDataToDisk`, cache sizes, and modified-file state.

## EA and Replacement Deletion Helpers

`FatRenameEAs` best-effort updates the owner filename in the EA set for non-FAT32 rename cases. It catches FAT exceptions internally and suppresses failures.

`FatDeleteFile` deletes a replacement target during rename. It removes matching open-but-clean FCBs from name tables, marks them delete-on-close with zero size and cluster state under paging I/O synchronization, then creates a temporary FCB for the target dirent, truncates allocation to zero, deletes the dirent, and deletes the temporary FCB.

## Key Dependencies

- File-object decoding and type taxonomy from `FatDecodeFileObject`.
- FCB/VCB resource acquisition helpers.
- Oplock package: `FsRtlCheckOplock`, `FsRtlCheckOplockEx`.
- Cache and memory manager: `CcSetFileSizes`, `CcFlushCache`, `CcPurgeCacheSection`, `MmCanFileBeTruncated`, `MmFlushImageSection`.
- Directory/name machinery: `FatLocateDirent`, `FatCreateNewDirent`, `FatDeleteDirent`, `FatConstructDirent`, `FatConstructNamesInFcb`, `FatSetFullFileNameInFcb`, `FatRemoveNames`.
- Tunnel cache: `FsRtlFindInTunnelCache`, `FatTunnelFcbOrDcb`.
- Notifications: `FatNotifyReportChange`, `FsRtlNotifyFullChangeDirectory`.

## Implementation Notes

This file encodes many filesystem correctness constraints:

- FAT timestamp precision and local-time conversion are handled explicitly.
- Rename is not transactional; the code documents the points where recovery is impossible and uses FCB invalidation as containment.
- Paging-file operations avoid acquiring normal FCB resources to prevent Memory Manager deadlocks.
- ReadyBoost/removable-media exceptions preserve mapping validation behavior across power transitions.
- Cache Manager state must be kept coherent whenever file size, allocation size, or VDL changes.
