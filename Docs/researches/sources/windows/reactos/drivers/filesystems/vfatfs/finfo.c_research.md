# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/finfo.c

Purpose: Implements IRP_MJ_QUERY_INFORMATION and IRP_MJ_SET_INFORMATION for VFAT files, including basic/standard/name/internal/network/EA/all information queries and position, disposition, allocation/EOF, basic metadata, and rename setters.

Key routines:
- `VfatGetStandardInformation`, `VfatGetBasicInformation`, `VfatGetNameInformation`, `VfatGetInternalInformation`, `VfatGetNetworkOpenInformation`, `VfatGetEaInformation`, and `VfatGetAllInformation` fill Windows file-information structures.
- `VfatSetPositionInformation` updates `FileObject->CurrentByteOffset`.
- `VfatSetBasicInformation` updates allowed attributes and FAT/FATX timestamp fields, writes the directory entry, and reports change notifications.
- `VfatSetDispositionInformation` marks/unmarks delete pending, rejecting read-only files, root, dot entries, mapped image sections, and non-empty directories.
- `vfatPrepareTargetForRename` opens/checks a rename target, enforces `ReplaceIfExists`, flushes/deletes replaceable targets, and rejects directories/read-only/open targets.
- `IsThereAChildOpened` and `VfatRenameChildFCB` protect directory renames with open descendants and update cached child paths after successful directory renames.
- `VfatSetRenameInformation` handles relative roots, fully qualified `\??\X:` names, target file objects, same-volume checks, in-place case-only rename, same-directory rename, cross-directory move, notification reporting, and child FCB path repair.
- `UpdateFileSize` synchronizes FCB sizes, on-disk file size fields, and cache-manager file sizes.
- `VfatSetAllocationSizeInformation` grows/shrinks allocation and EOF, allocates cluster chains, truncates/free chains, checks mapped-file truncation, updates FAT32 free counts, writes directory entries, and reports size changes.
- `VfatQueryInformation` and `VfatSetInformation` are the IRP entry points with resource acquisition/queueing behavior.

Implementation notes:
- Attribute setting masks to FAT-supported attributes and synthesizes `FILE_ATTRIBUTE_NORMAL` on query when no other basic attribute is set.
- FATX and FAT timestamp layouts are handled separately. Normal FAT access time stores only date.
- Delete disposition only marks pending; actual entry deletion is handled elsewhere during cleanup/close.
- Rename code distinguishes exact same-name success, case-only rename, replacement, and move across parent directories.
- Allocation growth from zero obtains a first cluster, then extends to the rounded target offset; truncation updates EOF/allocation first and then frees trailing clusters.

Dependencies and interactions:
- Calls directory-entry, FCB, FAT-chain, cache-manager, memory-manager, and notification helpers: `VfatUpdateEntry`, `VfatMoveEntry`, `vfatRenameEntry`, `VfatDelEntry`, `VfatIsDirectoryEmpty`, `OffsetToCluster`, `NextCluster`, `WriteCluster`, `MmCanFileBeTruncated`, `MmFlushImageSection`, `CcSetFileSizes`, and `vfatReportChange`.
- Fast I/O basic/standard query callbacks delegate into functions defined here.

Notable limitations and risks:
- `FileAlternateNameInformation` is not implemented, and most unsupported setters return `STATUS_NOT_SUPPORTED`.
- EA information always reports zero and logs missing FAT12/FAT16 support.
- The rename logic has assertions disabled via `NASSERTS_RENAME`, indicating historical fragility or unresolved reference-count edge cases.
- Some FAT-chain cleanup loops ignore or overwrite intermediate statuses, so disk-full or write failures may leave partially adjusted chains.
