# File Research: sources/windows/reactos/drivers/filesystems/fastfat/flush.c

## Purpose

`flush.c` implements FastFAT flush handling and lower-device flush propagation. It backs `IRP_MJ_FLUSH_BUFFERS`, flushes cached file data, directory metadata, FAT allocation metadata, whole volumes, selected FAT entry ranges, and selected dirent pages. It also contains helper completion routines for normal flush pass-through and for hijacking an existing IRP to send a lower-device flush.

The file is the bridge between FastFAT’s cache/metadata state and durable media state. It coordinates FCB/VCB locking, cache-manager flushes, BCB repinning, FAT page writeback, directory-entry writeback, dirty-volume cleanup, and target-device flushes.

## Main Entry Points

- `FatFsdFlushBuffers`
  - Dispatch wrapper for `IRP_MJ_FLUSH_BUFFERS`.
  - Enters the filesystem, establishes top-level IRP state, creates an IRP context, calls `FatCommonFlushBuffers`, and sends exceptions through FastFAT exception handling.

- `FatCommonFlushBuffers`
  - Common flush implementation for file, directory, root, and volume opens.
  - Posts to the FSP if the request cannot wait because `CcFlushCache` is synchronous.
  - On newer NT targets, charges disk-accounting flush activity to the originating thread or current thread.
  - Decodes the file object and dispatches by `TYPE_OF_OPEN`.

## Flush Behavior by Open Type

- `VirtualVolumeFile`, `EaFile`, `DirectoryFile`
  - Flush request is effectively a no-op at the FastFAT layer.

- `UserFileOpen`
  - Acquires the FCB exclusively and verifies it.
  - Calls `FatFlushFile` to flush the file data section.
  - On success, marks `FO_FILE_SIZE_CHANGED`, updates the dirent from the FCB, and records whether FAT flushing is required.
  - Walks parent DCBs upward, verifies each best effort, and flushes parent directory files so dirent updates reach disk.
  - Flushes FAT metadata through `FatFlushFat` when `FCB_STATE_FLUSH_FAT` is set.
  - Sets write-through on the IRP context so related metadata modifications complete with the request.

- `UserDirectoryOpen`
  - Non-root directory flushes do nothing directly.
  - Root directory flush falls through to whole-volume flushing.

- `UserVolumeOpen` and root DCB flush
  - Acquires the VCB exclusively.
  - Calls `FatFlushVolume`.
  - If the volume dirty flag is set, cancels pending clean-volume timer/DPC work.
  - Marks the volume clean when it was not mounted dirty.
  - Re-enables eject on removable media when no boot or paging file prevents it.

- Final pass-through
  - On normal termination, copies the IRP stack to the next driver and sends a flush to the target device.
  - `FatFlushCompletionRoutine` preserves pending state and maps lower `STATUS_INVALID_DEVICE_REQUEST` to success while restoring the FastFAT flush status.
  - On newer NT targets, data-only/no-sync flush minor functions skip the lower-device flush path.

## Helper Functions

- `FatFlushDirectory`
  - Non-recursively flushes a DCB tree.
  - Requires the VCB exclusively.
  - Temporarily forces write-through and wait flags if not already set.
  - First walks files, then directories, so file sizes and timestamps are reflected in directory entries before directories are flushed.
  - Skips the EA FCB and deleted files.
  - For file FCBs:
    - Acquires the FCB exclusively.
    - Verifies it best effort.
    - Applies pending truncate-on-close allocation truncation.
    - Reads the dirent and corrects `Dirent->FileSize` if it differs from the FCB.
    - Unpins the dirent BCB before flushing to avoid cache-manager/close deadlocks.
    - Calls `FatFlushFile`.
  - For DCBs:
    - Verifies best effort.
    - Calls `FatFlushFile` for good directory FCBs.
  - Aggregates flush errors but continues flushing the tree where possible.
  - Unpins repinned BCBs and restores temporarily modified IRP-context flags.

- `FatFlushFat`
  - Flushes dirty FAT pages for the whole volume.
  - Returns success immediately for write-protected volumes.
  - Verifies the VCB best effort and returns `STATUS_FILE_INVALID` if not good.
  - For FAT16/FAT32, walks FAT pages and uses `CcPinRead` with `PIN_IF_BCB` to touch only cached dirty ranges.
  - For FAT12, pins the whole FAT.
  - Marks pinned data dirty, repins, unpins, then unpins repinned BCBs with write-through and records I/O status.

- `FatFlushVolume`
  - Flushes all files/directories from the root DCB through `FatFlushDirectory`.
  - Flushes FAT metadata through `FatFlushFat`.
  - Re-enables eject for removable, non-boot, non-paging media.
  - Returns the first/last meaningful failed status while attempting both directory and FAT flush work.

- `FatFlushFile`
  - Calls `CcFlushCache` for the FCB section object pointers.
  - If the FCB was not deleted during the flush, takes the paging I/O resource exclusively to serialize with lazy writer activity.
  - If `FlushType == FlushAndInvalidate`, marks the FCB bad under paging-I/O synchronization.
  - Returns the cache flush status.

- `FatHijackIrpAndFlushDevice`
  - Reuses the current IRP by copying the stack location to the next stack, changing it to `IRP_MJ_FLUSH_BUFFERS`, installing `FatHijackCompletionRoutine`, and sending it to the target device.
  - Waits on an event if the lower driver returns pending.
  - Treats lower `STATUS_INVALID_DEVICE_REQUEST` as success.
  - Resets the IRP’s visible I/O status after the internal flush.

- `FatFlushFatEntries`
  - Flushes the cache range containing a FAT cluster run.
  - Computes byte offset/count differently for FAT12, FAT16, and FAT32.
  - Calls `CcFlushCache`, then uses `FatHijackIrpAndFlushDevice` to force the target device flush.
  - Normalizes and raises failures.

- `FatFlushDirentForFile`
  - Flushes the cache page containing an FCB’s parent-directory dirent.
  - Then hijacks the originating IRP to flush the target device.
  - Normalizes and raises failures.

- `FatFlushCompletionRoutine`
  - Completion routine for ordinary pass-through flush IRPs.
  - Marks pending when needed.
  - If lower flush succeeded or is unsupported, restores the FastFAT status supplied in the context.

- `FatHijackCompletionRoutine`
  - Signals the waiting event and returns `STATUS_MORE_PROCESSING_REQUIRED` so the hijacked IRP is not completed normally by the lower stack.

## Key Dependencies and Integration

- Uses `FatDecodeFileObject` to classify flush targets.
- Integrates with `FatVerifyFcb`, `FatVerifyVcb`, `FatUpdateDirentFromFcb`, `FatSetFileSizeInDirent` indirectly through dirent update paths, `FatTruncateFileAllocation`, `FatMarkVolume`, and media eject toggling.
- Uses cache-manager APIs: `CcFlushCache`, `CcPinRead`, `CcSetDirtyPinnedData`, `CcRepinBcb`, `CcUnpinData`, `CcUnpinRepinnedBcb`.
- Uses resource synchronization through FCB resources, VCB resources, and paging I/O resources.
- Uses lower-driver IRP forwarding for durable device flushes after filesystem cache flushes.

## Important Invariants

- Flushes that call cache manager synchronously must run in a waitable context.
- File data should be flushed before parent directories so dirent file sizes/times can be made durable.
- FAT metadata must be flushed when allocation state changed.
- Dirent BCBs are unpinned before file flushes because flush-triggered close can tear down parts of the tree.
- Lower devices that do not support flush are not treated as fatal for normal flush completion.
- Whole-volume flush requires exclusive VCB ownership.

## Notable Risks

- Flush paths deliberately continue after expected verification/corruption errors, so return status can represent a later aggregated failure while some objects were still flushed.
- Cache-manager flushes can cause FCB final close and deletion; code must check deleted-FCB state before touching or releasing FCBs.
- `FatHijackIrpAndFlushDevice` mutates an existing IRP stack for internal use and must restore visible I/O status afterward.
- FAT12 whole-FAT flushing is heavier than FAT16/FAT32 page-by-page dirty-range flushing.
- Correct durability depends on both FastFAT cache flushes and successful target-device flush propagation where supported.
