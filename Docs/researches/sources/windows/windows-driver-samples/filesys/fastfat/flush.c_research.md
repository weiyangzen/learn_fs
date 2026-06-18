# File Research: sources/windows/windows-driver-samples/filesys/fastfat/flush.c

## Role

`flush.c` implements FastFAT flush handling for `IRP_MJ_FLUSH_BUFFERS` and internal helpers for flushing files, directories, FAT metadata, dirent pages, FAT-entry ranges, volumes, and target devices. It coordinates filesystem metadata, Cache Manager state, FAT dirty ranges, removable-media clean state, and pass-through device flushes.

## Dispatch Entry

`FatFsdFlushBuffers` is the FSD dispatch wrapper. It enters the filesystem, establishes top-level IRP state, creates an IRP context with `CanFsdWait`, calls `FatCommonFlushBuffers`, and handles exceptions through the FastFAT exception path.

## Common Flush Flow

`FatCommonFlushBuffers` decodes the `FILE_OBJECT` with `FatDecodeFileObject`.

Because `CcFlushCache` is synchronous, non-wait-capable requests are posted to the FSP with `FatFsdPostRequest`.

Open-type behavior:

- `VirtualVolumeFile`, `EaFile`, `DirectoryFile`: no-op flush.
- `UserFileOpen`: acquires the FCB exclusive, verifies it, flushes file data, updates the file dirent from the FCB, tracks whether FAT flushing is required, flushes parent DCB chain, optionally flushes the FAT, and sets write-through state.
- `UserDirectoryOpen`: non-root directories are no-op; root directory falls through to volume flush.
- `UserVolumeOpen`: acquires VCB exclusive and flushes the volume.

On Windows 8+, disk flush accounting charges the originating user thread or current thread.

After filesystem work completes normally, the IRP is copied to the next stack location and sent to the target device object unless Windows 8+ minor-function rules skip it for data-only/no-sync variants. `FatFlushCompletionRoutine` merges lower-driver status with the filesystem flush status and treats unsupported device flush as non-fatal.

## File Flush

`FatFlushFile` calls `CcFlushCache` for the FCB section object pointers. If the FCB was not deleted during the flush, it acquires and releases `PagingIoResource` to serialize with the lazy writer and ensure cached I/O completion. If `FlushType == FlushAndInvalidate`, it marks the FCB condition bad while holding paging I/O synchronization.

## Directory Tree Flush

`FatFlushDirectory` flushes a DCB subtree in two passes while the VCB is exclusive:

1. File pass:
   - Walks top-down.
   - For regular files other than the EA FCB and deleted files, acquires FCB exclusive.
   - Verifies FCB and skips bad ones.
   - If `FCB_STATE_TRUNCATE_ON_CLOSE` is set, truncates allocation to file size.
   - Reads the dirent, corrects `Dirent->FileSize` from FCB size when needed, unpins before flushing, then flushes the file.
   - Handles expected filesystem exceptions and continues flushing as much of the tree as possible.

2. Directory pass:
   - Flushes DCB/root DCB entries after files so file sizes and timestamps reach disk first.
   - Verifies each directory FCB and flushes good ones.

It temporarily forces `IRP_CONTEXT_FLAG_WRITE_THROUGH` and `IRP_CONTEXT_FLAG_WAIT` when absent, then restores them. It finally attempts `FatUnpinRepinnedBcbs`, capturing exceptions into the return status.

## FAT Flush

`FatFlushFat` flushes the volume FAT area.

Behavior:

- Returns success immediately for write-protected volumes.
- Verifies the VCB and returns `STATUS_FILE_INVALID` if not good.
- For FAT16/FAT32, walks the FAT page by page and pins only if a BCB exists (`PIN_IF_BCB`), avoiding reading the entire FAT just to flush clean ranges.
- For FAT12, pins the whole FAT because the FAT is small and 12-bit entry packing is less page-friendly.
- Marks pinned data dirty, repins, unpins, and unpins repinned BCBs with write-through.
- Captures expected FAT exceptions and continues where possible for page-walk mode.

## Volume Flush

`FatFlushVolume` skips write-protected volumes, then:

- Flushes all files and directories via `FatFlushDirectory`.
- Flushes the FAT via `FatFlushFat`.
- Unlocks removable media with `FatToggleMediaEjectDisable` if the volume is removable and not a boot/paging volume.

`FatCommonFlushBuffers` additionally handles clean-volume state after a volume flush: it cancels pending clean timers/DPCs, marks the volume clean when it was not mounted dirty, clears `VCB_STATE_FLAG_VOLUME_DIRTY`, and unlocks removable media.

## Target Device Flush Hijacking

`FatHijackIrpAndFlushDevice` is used when FastFAT needs to force a device flush but does not have a flush IRP.

It:

- Copies the current IRP stack to the next stack location.
- Changes the major function to `IRP_MJ_FLUSH_BUFFERS`.
- Installs `FatHijackCompletionRoutine`, which signals an event and returns `STATUS_MORE_PROCESSING_REQUIRED`.
- Calls the target device and waits if pending.
- Normalizes `STATUS_INVALID_DEVICE_REQUEST` to success.
- Clears the original IRP status/information before returning.

This helper is used by range-specific flush helpers below.

## Range-Specific Flush Helpers

`FatFlushFatEntries` flushes the FAT page/range containing a cluster run.

- Computes the byte offset from reserved FAT bytes.
- Accounts for FAT12 packed entries, FAT16 entries, and FAT32 entries.
- Calls `CcFlushCache` on the VCB section object pointers.
- Sends a hijacked target-device flush if cache flush succeeds.
- Raises normalized status on failure.

`FatFlushDirentForFile` flushes the page containing a file's dirent in its parent directory.

- Uses `Fcb->DirentOffsetWithinDirectory`.
- Flushes the parent DCB section object pointers for one `DIRENT`.
- Sends a hijacked target-device flush on success.
- Raises normalized status on failure.

## Completion Routines

`FatFlushCompletionRoutine` preserves pending state, treats lower-driver success or unsupported flush as allowing the original filesystem status to stand, and returns `STATUS_SUCCESS`.

`FatHijackCompletionRoutine` signals the waiting event and returns `STATUS_MORE_PROCESSING_REQUIRED` so the hijacked IRP is not completed normally by the lower stack.

## Key Dependencies

- File object classification: `FatDecodeFileObject`.
- Metadata update: `FatUpdateDirentFromFcb`, `FatTruncateFileAllocation`.
- Cache Manager: `CcFlushCache`, `CcPinRead`, `CcSetDirtyPinnedData`, `CcRepinBcb`, `CcUnpinRepinnedBcb`.
- Device stack: `IoCopyCurrentIrpStackLocationToNext`, `IoSetCompletionRoutine`, `IoCallDriver`.
- Volume state: `FatMarkVolume`, clean-volume timer/DPC, removable-media eject disable.
- Verification and exception normalization: `FatVerifyFcb`, `FatVerifyVcb`, `FatExceptionFilter`, `FatNormalizeAndRaiseStatus`.

## Implementation Notes

The file prioritizes durability ordering: user-file flushes push file data, then dirent updates, parent directories, FAT metadata, and finally lower device flushes. Directory subtree flushing writes files before directories so size and timestamp metadata is coherent. FAT flushing avoids unnecessary FAT32 reads by relying on dirty BCB presence. Unsupported lower-device flush is normalized to success, matching the Windows storage-stack convention that some devices do not implement explicit flush.
