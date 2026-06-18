# File Research: sources/windows/reactos/drivers/filesystems/udfs/fscntrl.cpp

`fscntrl.cpp` implements `IRP_MJ_FILE_SYSTEM_CONTROL` for UDFS. It handles user FSCTLs, mount, verify delegation, blank/raw mount fallback, root FCB construction, eject-waiter startup, VCB cleanup, volume lock/unlock/dismount, volume bitmaps, retrieval pointers, dirty checks, and invalidation.

Dispatch and FSCTL handling:
- `UDFFSControl()` allocates IRP context and delegates to `UDFCommonFSControl()`.
- `UDFCommonFSControl()` dispatches `IRP_MN_USER_FS_REQUEST`, `IRP_MN_MOUNT_VOLUME`, and `IRP_MN_VERIFY_VOLUME`; verify is delegated to `UDFVerifyVolume()`.
- `UDFUserFsCtrlRequest()` rejects oplock FSCTLs, supports `FSCTL_INVALIDATE_VOLUMES`, `FSCTL_IS_VOLUME_DIRTY`, `FSCTL_ALLOW_EXTENDED_DASD_IO`, `FSCTL_DISMOUNT_VOLUME`, `FSCTL_IS_VOLUME_MOUNTED`, `FSCTL_FILESYSTEM_GET_STATISTICS`, `FSCTL_LOCK_VOLUME`, `FSCTL_UNLOCK_VOLUME`, `FSCTL_IS_PATHNAME_VALID`, `FSCTL_GET_VOLUME_BITMAP`, and `FSCTL_GET_RETRIEVAL_POINTERS`.

Mount path:
- `UDFMountVolume()` validates target device type and registry policy, handles removable-media check-verify/test-unit-ready spin-up, optionally locks media removal, creates the volume device object, initializes the VCB, reads disk geometry/UDF structures, initializes the write cache, and performs `UDFVInit()` plus disk verification.
- On normal media it selects cache mode based on media class/read-only/write mode, completes mount with `UDFCompleteMount()`, starts the eject waiter for writable media, fills VPB serial/label fields, marks `UDF_VCB_FLAGS_VOLUME_MOUNTED`, registers shutdown notification, and signals mount events.
- On failed UDF recognition it may attempt raw/blank mount unless ISO9660 is present; `UDFBlankMount()` creates a synthetic root containing a `Blank.CD` entry.
- Failure cleanup unlocks removable media, resets the device driver when needed, restores verify state, dismounts partial VCBs, deletes temporary volume devices, or passes the mount IRP down to a lower filesystem filter device.

Mount completion and residual cleanup:
- `UDFCompleteMount()` allocates the root FCB/name/file info, opens the root directory, initializes root NT FCB state, opens system stream directory and special files such as non-allocatable space and UID mapping, reads disk-specific config stream data, clears mount-time modified flags, initializes root common FCB header, and assigns ACLs.
- `UDFBlankMount()` builds a minimal root directory index for blank/raw media and disables fast I/O.
- `UDFCloseResidual()` releases special mount-time references such as non-allocatable file info, UID map, VAT, system stream directory, and root FCB chains.
- `UDFCleanupVCB()` frees VCB-owned caches, allocation bitmaps, statistics, labels, target names, buffers, write parameters, errors, and track maps.
- `UDFScanForDismountedVcb()` walks global VCBs and calls `UDFCheckForDismount()` for dismounting or unmounted residual VCBs.

Volume control helpers:
- `UDFStartEjectWaiter()` locks removable writable media, allocates an eject wait context, and queues `UDFEjectReqWaiter()`.
- `UDFIsVolumeMounted()` validates the open, verifies the VCB unless raw/locked, and returns success.
- `UDFGetStatistics()` copies per-processor filesystem statistics from the VCB.
- `UDFIsPathnameValid()` walks each path component, enforcing UDF name length and `UDFIsNameValid()`.
- `UDFLockVolume()` closes delayed files, verifies the VCB, flushes the logical volume, and locks only when open/reference counts indicate no other users.
- `UDFUnlockVolume()` clears VPB/UDFS lock state when the locker matches; the non-locked branch assigns multiple statuses and ultimately returns `STATUS_VOLUME_DISMOUNTED`.
- `UDFDismountVolume()` requires a locked volume with only residual references, runs `UDFDoDismountSequence()`, clears mounted/write-security state, and stops the eject waiter.
- `UDFGetVolumeBitmap()` validates user buffers, reports `VOLUME_BITMAP_BUFFER` data from `FSBM_Bitmap`, and protects access with `VCBResource`.
- `UDFGetRetrievalPointers()` validates/probes buffers and converts UDF extent mappings from `UDFReadFileLocation__()` into NT retrieval-pointer extents.
- `UDFIsVolumeDirty()` reports `VOLUME_IS_DIRTY` when the original integrity type is open.
- `UDFInvalidateVolumes()` requires `SeTcbPrivilege`, swaps in a fresh VPB for the target device, finds matching mounted VCBs, disables delayed close, dismounts them, stops eject waiting, and scans for final VCB teardown.

Notable behavior and dependencies:
- This file is tightly coupled to lower storage IOCTLs, VPB state, removable-media locking, UDF registry/config policy, UDF_INFO mount helpers, write-cache setup, delayed-close queues, and global VCB management.
- It supports both direct UDFS filesystem device objects and filter-device mount forwarding to a lower filesystem.
- The mount path contains several recovery/fallback paths: retry check-verify, raw mount, blank mount, device-driver reset, and lower-driver handoff.
