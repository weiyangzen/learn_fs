# File Research: sources/windows/reactos/drivers/filesystems/fastfat/fsctrl.c

## Scope

This file implements ReactOS fastfat file-system-control handling, adapted from the Microsoft fastfat codebase. It covers IRP_MJ_FILE_SYSTEM_CONTROL dispatch, FAT volume mount and verify, user FSCTL routing, oplock FSCTLs, volume lock/unlock/dismount/dirty state handling, mounted-volume invalidation, retrieval-pointer and bitmap queries, defrag move-file support, boot-area metadata queries, handle marking, purge-failure mode, zero-on-deallocate, volume-label verification helpers, and scaled wrappers around FsRtl large MCBs.

## Public And Internal APIs Covered

- Dispatch entry points: `FatFsdFileSystemControl()` and `FatCommonFileSystemControl()`.
- Mount and verify path: `FatMountVolume()`, `FatVerifyVolume()`, `FatIsBootSectorFat()`, `FatIsMediaWriteProtected()`, `FatPerformVerifyDiskRead()`, `FatSearchBufferForLabel()`, and `FatVerifyLookupFatEntry()`.
- User FSCTL switch: `FatUserFsCtrl()` routes oplock, lock, unlock, dismount, dirty, mounted, pathname-valid, BPB/statistics, bitmap, retrieval-pointer, move-file, extended DASD, mark-handle, purge-failure, and zero-on-deallocate requests.
- Volume state operations: `FatLockVolume()`, `FatUnlockVolume()`, `FatLockVolumeInternal()`, `FatUnlockVolumeInternal()`, `FatDismountVolume()`, `FatDirtyVolume()`, `FatIsVolumeDirty()`, `FatIsVolumeMounted()`, `FatInvalidateVolumes()`, `FatScanForDismountedVcb()`, and `FatFlushAndCleanVolume()`.
- Query/metadata FSCTLs: `FatQueryRetrievalPointers()`, `FatQueryBpb()`, `FatGetStatistics()`, `FatGetVolumeBitmap()`, `FatGetRetrievalPointers()`, `FatAllowExtendedDasdIo()`, `FatGetRetrievalPointerBase()`, `FatGetBootAreaInfo()`.
- Defrag and allocation movement: `FatMoveFile()`, `FatMoveFileNeedsWriteThrough()`, `FatComputeMoveFileParameter()`, and `FatComputeMoveFileSplicePoints()`.
- Handle and mode controls: `FatMarkHandle()`, `FatSetPurgeFailureMode()`, and `FatSetZeroOnDeallocate()`.
- MCB wrappers: `FatNonSparseMcb()`, `FatAddMcbEntry()`, `FatLookupMcbEntry()`, `FatLookupLastMcbEntry()`, `FatGetNextMcbEntry()`, and `FatRemoveMcbEntry()`.

## Control Flow And Behavior

- `FatFsdFileSystemControl()` establishes top-level IRP state, makes mount/verify waitable, special-cases `FSCTL_INVALIDATE_VOLUMES` arriving on the filesystem device object, creates an IRP context for normal volume requests, and delegates to the common worker under exception handling.
- `FatCommonFileSystemControl()` switches on minor function: user FSCTL, mount volume, verify volume, or invalid request. Mount completion is performed at this level so recursive mount paths do not complete the same IRP twice.
- `FatMountVolume()` validates removable media presence, rejects non-data CD tracks, queries partition and geometry information, creates and initializes a volume device object and VCB, temporarily clears `DO_VERIFY_VOLUME`, reads and validates the boot sector, unpacks the BPB, rejects OS/2 Boot Manager lookalikes, checks sector-size consistency, initializes allocation support, creates the root DCB, loads the volume label, detects remounts by matching old unmounted VCBs by serial/label/BPB/real device, creates legacy EA support on FAT12/16, reads dirty/write-protect state, handles boot-volume eject disable, references the root directory stream, dereferences the target device object, and emits mount notification outside synchronization.
- Remount swaps the target device object into the old VCB, reattaches the old VPB to the real device, updates the change count, reinitializes the old volume-file cache and allocation support, checks dirty/write-protect state, and marks the transient new VCB bad for teardown.
- `FatVerifyVolume()` serializes with global and VCB resources, checks whether verification is still required, re-issues low-level media checks, compares sector size, boot signature, serial number, BPB contents, and root volume label, and then either purges/rebuilds allocation support on success or tears down cache/allocation state and marks the VCB not mounted on wrong volume.
- `FatIsBootSectorFat()` performs sanity checks on boot jump opcode, sector size, cluster size, reserved sectors, FAT count, total sectors, FAT32 FAT size/version, media byte, FAT12/16 root entries, and disabled FAT32 mirroring.
- `FatUserFsCtrl()` forces waitability for user-mode METHOD_NEITHER calls and dispatches supported FSCTL codes to the appropriate helper, rejecting unknown codes with `STATUS_INVALID_DEVICE_REQUEST`.
- `FatOplockRequest()` accepts file opens and, on newer builds, read/read-handle directory oplocks. It validates modern request/ack buffers, acquires FCB/VCB resources according to request type, rejects incompatible delete-pending requests, derives an oplock-count blocker from file locks or unclean count, calls `FsRtlOplockFsctrl()`, and updates `IsFastIoPossible`.
- Volume lock requires a user volume open with manage-volume access. It notifies listeners, acquires the VCB exclusively, flushes FAT and referenced file objects, closes EA state, waits for lazy writer activity twice, drains delayed closes, then sets `VPB_LOCKED`, `VPB_DIRECT_WRITES_ALLOWED`, `VCB_STATE_FLAG_LOCKED`, and the locking file object only if open counts and VPB references show no conflicting users.
- Unlock clears the VPB/VCB lock flags only when the caller matches the file object that owns the lock. A missing system lock is tolerated by the internal helper when the optional file object is absent.
- Forced dismount now does not require a prior volume lock. It rejects boot/paging volumes and already-dismounted volumes, notifies, acquires global and whole-volume synchronization, calls `FatFlushAndCleanVolume(FlushAndInvalidate)`, flags the CCB to complete physical dismount on cleanup, marks the VCB bad and volume dismounted, and enables direct writes in the VPB.
- Dirty-state FSCTLs validate user volume opens, manage-volume access where required, suppress popups, verify media, mark or report mounted-dirty state, and fill the `VOLUME_IS_DIRTY` output bit from internal state.
- `FatInvalidateVolumes()` is privileged by `SeTcbPrivilege`, takes a handle to identify the real device, walks all VCBs for that real device under the global resource, swaps in a fresh VPB when needed, marks matching VCBs bad, marks all FCBs bad, purges referenced file objects, and checks for dismount.
- `FatQueryRetrievalPointers()` is a kernel-only paging-file query using METHOD_NEITHER buffers. It validates the requested map size, walks the file MCB, allocates nonpaged mapping pairs, and returns `[sector count, LBO]` pairs terminated by zero.
- `FatGetVolumeBitmap()` requires a manage-volume handle, probes METHOD_NEITHER buffers, aligns starting LCN down to a byte boundary, returns a bitmap from the cached free-cluster bitmap when one window covers the FAT, or scans FAT entries for multi-window volumes.
- `FatGetRetrievalPointers()` supports user file, directory, and manage-volume opens. File/directory calls return extent mappings from the FCB MCB; volume calls return bad-block mappings from `BadBlockMcb`. It verifies allocation size hints, handles root-directory FAT32 directory sizing, probes buffers, starts at the containing run for the input VCN, and returns overflow when the output extent array is exhausted.
- `FatMoveFile()` implements FSCTL_MOVE_FILE defrag relocation from a manage-volume DASD handle and a referenced target file/directory handle. It validates LCN/VCN/count ranges, rejects cross-volume and invalid directory moves, optionally disables write-through for zero-VDL files, opens directory stream files when needed, loops in bounded buffer-sized chunks, allocates exact target clusters, optionally copies valid data by direct device I/O, splices FAT chains or parent dirents, flushes critical metadata and device cache, deallocates old clusters, updates the file MCB, and uses `MoveFileEvent` plus paging I/O resource transitions to block concurrent I/O during allocation replacement.
- `FatComputeMoveFileParameter()` bounds the requested chunk by allocation size, buffer alignment, contiguous source run length, and valid-data length, returning how many bytes need reallocation versus actual data copy.
- `FatComputeMoveFileSplicePoints()` identifies the previous source cluster, new target start, final target cluster, and next source cluster after the moved span, while building an MCB describing the old allocation that must later be freed.
- `FatMarkHandle()` supports file and directory handles, validates mark bits and USN source flags for compatibility, requires kernel mode, manage-volume access, or a same-volume DASD handle for privileged cluster protection, and sets `CCB_FLAG_DENY_DEFRAG` plus `FCB_STATE_DENY_DEFRAG`.
- `FatFlushAndCleanVolume()` is shared by dismount/PNP-style callers. It flushes volume state when requested, closes EA state, flushes the device, purges volume and referenced file-object cache, cancels pending clean timers, marks the volume clean if allowed and not mounted dirty, and reenables eject on removable non-boot media.
- Newer FSCTL helpers return the file-area sector base, FAT boot-sector locations, kernel-only purge-failure reference-count changes, and per-file zero-on-deallocation state.

## State And Data Structures

- Volume/device state: `VOLUME_DEVICE_OBJECT`, `VCB`, `VPB`, `FatData.VcbQueue`, target device object, real device object, swap VPB, volume GUID/path on newer builds, change count, and VCB condition/state flags.
- On-disk metadata: packed boot sector, unpacked BPB, FAT32 FSInfo, root directory label dirents, FAT entries, boot-area offsets, allocation support, bad-block MCB, free-cluster bitmap, dirty FAT MCB, and stashed FAT12/16 first 0x24 boot bytes.
- File/directory state: `FCB`, `DCB`, `CCB`, root DCB, EA FCB, file object references, FCB MCB, directory stream file object, first cluster, allocation/file/valid-data sizes, oplock object, file-lock object, and fast-I/O state.
- Synchronization: global resource, VCB/whole-volume/FCB resources, paging I/O resource, VPB spin lock, stack events, lazy writer wait, BCB pinning/repinning, `MoveFileEvent`, and top-level IRP markers.
- User buffers: METHOD_BUFFERED system buffers for many FSCTLs; METHOD_NEITHER input/output buffers for bitmap/retrieval APIs; explicit probing and `FatMapUserBuffer()` for user-mode pointers.

## Dependencies

- NT I/O manager and storage APIs: IRPs, VPBs, device objects, `IoCreateDevice`, `IoCallDriver`, synchronous FSD requests, device I/O controls, removable-media verify, geometry and partition queries, and volume notifications.
- Cache manager and FsRtl: cache map initialization/uninitialization, cache purge, lazy writer wait, oplock package, file locks, large MCB package, volume events, and filesystem entry/exit helpers.
- Fastfat internals: VCB/FCB/CCB decoding and synchronization, boot/BPB unpacking, allocation support setup/teardown, FAT entry allocation/deallocation/flush, volume dirty marking, root DCB creation, label lookup, EA close, file-object purge, delayed closes, dismount checking, and exception handling.
- Security/object manager: privilege checks, handle-to-file-object references, kernel/user mode validation, WoW64 thunking for handle-sized FSCTL inputs.

## Risks And Invariants

- Mount/remount correctness depends on exact cleanup in SEH finally blocks: transient VCBs, VPBs, BCBs, target-device references, and temporarily cleared verify bits must be restored or released exactly once.
- Verify must make the right distinction between `STATUS_WRONG_VOLUME`, hard I/O errors, and raw-mount-allowed failures; stale cache/allocation state is explicitly purged or torn down after verification.
- Volume lock/dismount relies on open-count, VPB-reference, lazy-writer, and delayed-close ordering. Racing cleanup can raise `STATUS_FILE_CLOSED`, which the lock path handles specially.
- User FSCTLs using METHOD_NEITHER must be synchronous and carefully probed. Several helpers rely on `IRP_CONTEXT_FLAG_WAIT` because input handles and user buffers cannot safely outlive the caller context.
- Defrag relocation is a high-risk metadata update path: data copy, new FAT allocation, two FAT splices or dirent update, old-cluster deallocation, MCB replacement, BCB flush, and device flush must preserve recoverability if an exception occurs mid-operation.
- `FatMoveFile()` intentionally drops the FCB between chunks and uses `MoveFileEvent` to avoid holding paging I/O across flushes. The event/resource protocol is central to preventing concurrent I/O and deadlocks.
- MCB wrappers scale logical byte offsets by sector size and translate sparse `-1` LBNs to legacy zero behavior; overflow and 4GiB edge cases are explicitly handled.
- Some APIs are compatibility stubs or compatibility-preserving behavior: pathname-valid always succeeds, USN source flags are ignored, BPB query only exists for stashed FAT12/16 boot bytes, and unsupported/invalid handles often return legacy NTSTATUS values.
