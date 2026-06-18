# File Research: sources/windows/windows-driver-samples/filesys/fastfat/fsctrl.c

## Purpose

`fsctrl.c` implements FastFAT file-system control handling. It covers the FSD/FSP dispatch path for `IRP_MJ_FILE_SYSTEM_CONTROL`, volume mount and verify, user FSCTL routing, volume lock/unlock/dismount/dirty operations, allocation-map queries, defrag move-file support, and several mount/verify helpers.

It is one of the main volume-lifecycle files in FastFAT: it creates VCB/device state at mount, validates removable media changes, tears down or remounts old VCBs, and exposes filesystem-control APIs used by defrag, raw volume tools, boot/volume query callers, oplocks, and cache coherency paths.

## Dispatch and MCB Wrappers

- `FatFsdFileSystemControl`
  - Top-level FSD dispatch for file-system controls.
  - Establishes filesystem context and top-level IRP state.
  - Special-cases `FSCTL_INVALIDATE_VOLUMES` on the filesystem device object.
  - Creates an IRP context and calls `FatCommonFileSystemControl`.
  - Uses FastFAT exception processing for cleanup and completion.

- `FatCommonFileSystemControl`
  - Switches on minor function:
    - `IRP_MN_USER_FS_REQUEST` -> `FatUserFsCtrl`
    - `IRP_MN_MOUNT_VOLUME` -> `FatMountVolume`
    - `IRP_MN_VERIFY_VOLUME` -> `FatVerifyVolume`
  - Completes invalid minor requests with `STATUS_INVALID_DEVICE_REQUEST`.

- `FatNonSparseMcb`, `FatAddMcbEntry`, `FatLookupMcbEntry`, `FatLookupLastMcbEntry`, `FatGetNextMcbEntry`, `FatRemoveMcbEntry`
  - Wrap `FsRtl` large-MCB APIs.
  - Scale byte offsets/counts by the volume sector size.
  - Preserve old FastFAT semantics around unused `-1` LBN entries.
  - Defend debug builds against unexpected sparse entries outside `DirtyFatMcb`.
  - Handle 4 GiB edge cases where shifted byte counts overflow back to zero.

## Mount and Verify

- `FatMountVolume`
  - Performs FAT recognition and VCB creation.
  - Checks removable-media change count with `IOCTL_DISK_CHECK_VERIFY`.
  - Rejects CD media without a data track.
  - Queries partition info and drive geometry.
  - Creates the volume device object, initializes the VCB, temporarily clears `DO_VERIFY_VOLUME`, reads the boot sector, and validates it with `FatIsBootSectorFat`.
  - Extracts BPB, serial number, FAT32 FSInfo sanity, volume GUID/path, and FAT12/16 stashed BPB bytes for `FSCTL_QUERY_FAT_BPB`.
  - Rejects OS/2 Boot Manager partitions that mimic FAT.
  - Verifies BPB sector size against device geometry.
  - Builds the root DCB, locates/converts the volume label, and scans existing VCBs for a remount match.
  - Remount path swaps target devices, restores the old VPB/VCB, reinitializes cache/allocation support, checks dirty/write-protected state, and discards the temporary VCB.
  - New-mount path creates the hidden EA data FCB for non-FAT32, checks dirty/write-protected state, handles boot/paging removable media eject locking, and sends mount notification.

- `FatVerifyVolume`
  - Verifies that current media still matches the mounted VCB.
  - Serializes verification under the global and VCB resources.
  - Rechecks removable-media change count, CD data track, drive geometry, boot sector FAT validity, serial number, BPB equality, and volume label.
  - FAT12/16 label verification reads the fixed root directory; FAT32 walks the root directory cluster chain using `FatVerifyLookupFatEntry`.
  - On success, flushes/purges cached data, tears down and rebuilds allocation support, checks dirty/write-protected state, and clears `DO_VERIFY_VOLUME`.
  - On wrong volume, purges without flushing, uninitializes the volume-file cache map, tears down allocation support, marks the VCB `VcbNotMounted`, and prepares for later remount/deletion.
  - Always closes/reset EA state and marks FCBs as needing verification when a real verification occurred.

- `FatIsBootSectorFat`
  - Validates the unpacked BPB and boot jump.
  - Checks sector size, cluster size, reserved sectors, FAT count, total sectors, FAT32 FAT/version fields, media byte, root-entry requirements for FAT12/16, and rejects FAT32 mirror-disabled volumes.

- `FatIsMediaWriteProtected`
  - Sends `IOCTL_DISK_IS_WRITABLE`.
  - Returns true only for `STATUS_MEDIA_WRITE_PROTECTED`; allocation failure or other errors are treated as writable.

- `FatPerformVerifyDiskRead`
  - Builds direct synchronous read IRPs to the target device.
  - Sets `SL_OVERRIDE_VERIFY_VOLUME`.
  - Converts read failures either to a false return or raised FastFAT status depending on `ReturnOnError`.

- `FatVerifyLookupFatEntry`
  - FAT32 verify helper.
  - Reads a page containing a FAT entry directly from disk and returns the raw entry value.

## User FSCTL Handling

- `FatUserFsCtrl`
  - Dispatches user FSCTL codes.
  - Forces synchronous handling for user-mode `METHOD_NEITHER` controls.
  - Routes oplocks, lock/unlock/dismount, dirty/mounted/pathname checks, retrieval/bitmap queries, BPB/statistics queries, move-file, extended DASD I/O, boot area/retrieval-base, mark-handle, purge-failure mode, and zero-on-deallocation.
  - Completes unsupported FSCTLs with `STATUS_INVALID_DEVICE_REQUEST`.

- `FatOplockRequest`
  - Handles legacy and Win7+ oplock FSCTLs.
  - Permits file oplocks and, on newer builds, shared directory oplocks.
  - Acquires FCB/VCB resources according to request vs acknowledgement.
  - Denies incompatible requests on delete-pending files or byte-range-locked files.
  - Delegates to `FsRtlOplockFsctrl` and updates `IsFastIoPossible`.

## Volume State FSCTLs

- `FatLockVolume`
  - Requires a user volume open with `CCB_FLAG_MANAGE_VOLUME_ACCESS`.
  - Sends lock notification, acquires the VCB, and calls `FatLockVolumeInternal`.
  - Sends failure notification if the lock cannot be taken.

- `FatLockVolumeInternal`
  - Flushes FAT and referenced file objects, closes EA state, waits for lazy writer activity twice, drains delayed closes, and then checks VPB refs/open counts.
  - Sets `VPB_LOCKED`, `VPB_DIRECT_WRITES_ALLOWED`, `VCB_STATE_FLAG_LOCKED`, and records the locking file object.
  - May mark the volume clean if dirty state is only pending and no dirty cache data remains.

- `FatUnlockVolume` / `FatUnlockVolumeInternal`
  - Require a managed volume open.
  - Clear VPB direct-write/locked state only when the caller owns the lock.
  - Notify `FSRTL_VOLUME_UNLOCK` on success.

- `FatDismountVolume`
  - Requires a managed user volume open.
  - Rejects boot/paging volumes and already dismounted volumes.
  - Sends dismount notification, acquires global/volume state, flushes and invalidates through `FatFlushAndCleanVolume`, marks the CCB for complete dismount on cleanup, marks the VCB bad/dismounted, and enables direct volume writes.
  - Calls `FsRtlDismountComplete` on newer builds.

- `FatDirtyVolume`
  - Requires a managed volume open.
  - Verifies the VCB with popups disabled, sets mounted-dirty state, and marks the on-disk volume dirty.

- `FatIsVolumeDirty`
  - Requires a user volume open.
  - Maps the caller output buffer from system buffer or MDL.
  - Verifies VCB and returns `VOLUME_IS_DIRTY` from in-memory mounted-dirty state.

- `FatIsVolumeMounted`
  - Verifies the decoded VCB and returns success if still mounted.

- `FatIsPathnameValid`
  - Currently a no-op success path because a stricter previous implementation could falsely reject valid creatable names.

- `FatAllowExtendedDasdIo`
  - Requires a managed volume open.
  - Sets `CCB_FLAG_ALLOW_EXTENDED_DASD_IO` so the handle may read beyond the normal volume-file end.

- `FatSetZeroOnDeallocate`
  - Requires a writable user file open.
  - Rejects read-only/write-protected cases.
  - Acquires the FCB and sets `FCB_STATE_ZERO_ON_DEALLOCATION`.

## Query FSCTLs

- `FatQueryBpb`
  - Returns the stashed first `0x24` bytes of the FAT12/16 boot sector.
  - Fails if the stash was not kept, such as FAT32.

- `FatGetStatistics`
  - Copies per-processor `FILE_SYSTEM_STATISTICS` from the VCB.
  - Returns `STATUS_BUFFER_OVERFLOW` when the caller buffer is shorter than all processor records.

- `FatGetVolumeBitmap`
  - Requires a managed volume open.
  - Validates/probes `STARTING_LCN_INPUT_BUFFER` and `VOLUME_BITMAP_BUFFER`.
  - Returns allocation bitmap bytes from the in-memory free-cluster bitmap when one FAT window covers the volume, or scans FAT entries otherwise.
  - Starts on an 8-cluster-aligned boundary and returns `STATUS_BUFFER_OVERFLOW` if output is partial.

- `FatQueryRetrievalPointers`
  - Kernel-only paging-file query.
  - Takes requested map size and returns nonpaged mapping pairs `[sector count, LBO]`.
  - Uses the file MCB and fails corrupt/unexpected missing mappings.

- `FatGetRetrievalPointers`
  - Implements public retrieval-pointer query for file, directory, or managed volume opens.
  - For files/directories, verifies and uses the file MCB; for volume handles, returns bad-cluster MCB extents.
  - Converts VBO/LBO byte runs to VCN/LCN cluster extents.
  - Handles output exhaustion with partial `ExtentCount` and `STATUS_BUFFER_OVERFLOW`.

- `FatGetRetrievalPointerBase`
  - Requires a managed volume open.
  - Returns the sector offset to the FAT file area.

- `FatGetBootAreaInfo`
  - Requires a managed volume open.
  - Returns boot-sector locations: sector 0 for FAT12/16, sectors 0 and 6 for FAT32.

## Move File / Defrag Support

- `FatMoveFile`
  - Implements `FSCTL_MOVE_FILE` for a managed DASD handle.
  - Supports WOW64 thunking of `MOVE_FILE_DATA`.
  - References the target file handle, confirms same volume, accepts file opens and allowed directory opens, and rejects unsafe root/first-cluster directory moves.
  - Moves allocation in chunked passes using temporary source/target MCBs and a nonpaged transfer buffer.
  - Allocates target clusters exactly at the requested LCN, reads/writes live data when required, writes through the device, splices FAT chains, updates the parent dirent when moving a file’s first cluster, deallocates orphaned source clusters, flushes device state, and updates the file MCB.
  - Uses `MoveFileEvent` plus paging I/O resource choreography so file I/O waits during the critical allocation switch without holding paging I/O across flushes.
  - On failure, deallocates newly allocated space, unpins metadata, clears/invalidates the file MCB and allocation-size hint when needed, releases resources, and dereferences the file object.

- `FatMoveFileNeedsWriteThrough`
  - Adjusts IRP context write-through behavior for zero-VDL files to avoid unnecessary FAT flushes.

- `FatComputeMoveFileParameter`
  - Bounds the current move chunk by allocation size, transfer-buffer size, contiguous source run length, and valid-data length.
  - Returns bytes to reallocate, bytes needing data copy, and source LBO.

- `FatComputeMoveFileSplicePoints`
  - Computes FAT chain splice points around the source range.
  - Builds an MCB describing source allocation to deallocate after the new chain is committed.

- `FatMarkHandle`
  - Supports handle-level defrag protection.
  - Allows `MARK_HANDLE_PROTECT_CLUSTERS` after access checks using manage-volume privilege, kernel mode, or a valid volume handle.
  - Sets `CCB_FLAG_DENY_DEFRAG` and `FCB_STATE_DENY_DEFRAG`.

## Invalidate, Flush, and Cleanup Helpers

- `FatInvalidateVolumes`
  - Special filesystem-device FSCTL requiring `SeTcbPrivilege`.
  - Resolves a supplied file handle to a real device.
  - Walks all mounted VCBs on that device, swaps out mounted VPBs if needed, marks VCBs bad, marks all FCBs bad, purges referenced file objects without flushing, and checks for dismount.

- `FatFlushAndCleanVolume`
  - Shared dismount/PNP flush helper.
  - Flushes volume data if requested, closes EA state, flushes the lower device, purges volume/file cache sections unless told not to, cancels clean-volume timers, marks the disk clean when allowed, and releases removable-media eject disable where appropriate.

- `FatSetPurgeFailureMode`
  - Kernel-only file FSCTL on newer builds.
  - Reference-counts an FCB purge-failure mode that makes coherency purge failures propagate instead of being ignored.

- `FatSearchBufferForLabel`
  - Scans root-directory dirents for a volume label.
  - Converts the 8.3 OEM label to Unicode and compares it against the VPB label.
  - Distinguishes no label, matching label, non-matching label, and conversion errors.

- `FatScanForDismountedVcb`
  - Walks the global VCB queue under the global resource.
  - Opportunistically acquires VCBs and calls `FatCheckForDismount` to delete stale dismounted volumes.

## Integration Points

`fsctrl.c` sits at the boundary between FastFAT metadata state and Windows I/O manager APIs. It depends on VPB flags/reference counts, VCB/FCB resource ordering, Cache Manager purge/flush APIs, Memory Manager section behavior, direct device IOCTLs, lower-device read/write/flush IRPs, FSRTL oplock and notification helpers, FAT allocation helpers, FAT dirent helpers, and FastFAT exception-processing conventions.

## Risk Notes

- Mount/remount and verify depend on precise VPB, VCB, target-device, and reference-count transitions; ordering mistakes can leave stale volumes reachable or cause premature deletion.
- `FatMoveFile` is especially delicate: data copy, FAT splicing, dirent update, cache flushing, MCB update, and error unwind must stay consistent across failures.
- User-buffer handling is mixed across system buffers, MDLs, and `METHOD_NEITHER`; the file carefully forces wait/probes buffers where needed.
- The code intentionally treats some I/O errors as wrong-volume or unrecognized-volume so RAW/CDFS and removable media flows can proceed.
- FAT32 verification reads FAT entries directly from disk while allocation support may be torn down/rebuilt, so synchronization assumptions are central.
