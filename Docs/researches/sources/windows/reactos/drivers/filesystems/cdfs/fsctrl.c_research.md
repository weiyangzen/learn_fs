# File Research: sources/windows/reactos/drivers/filesystems/cdfs/fsctrl.c

## Purpose

`fsctrl.c` implements CDFS file-system-control handling: mount, verify, user FSCTL dispatch, oplocks, volume lock/unlock/dismount, volume dirty/mounted/path queries, volume invalidation, extended DASD I/O, remount detection, and ISO/Joliet volume descriptor scanning.

It also defines global mount behavior flags:

- `CdDisable`: disables CDFS mounting.
- `CdNoJoliet`: disables Joliet supplementary descriptor selection.

## Top-Level Dispatch

- `CdCommonFsControl`: dispatches by FSCTL minor function:
  - `IRP_MN_USER_FS_REQUEST` -> `CdUserFsctl`
  - `IRP_MN_MOUNT_VOLUME` -> `CdMountVolume`
  - `IRP_MN_VERIFY_VOLUME` -> `CdVerifyVolume`
  - others -> `STATUS_INVALID_DEVICE_REQUEST`

- `CdUserFsctl`: dispatches user FSCTL codes:
  - Oplock FSCTLs -> `CdOplockRequest`
  - `FSCTL_LOCK_VOLUME` -> `CdLockVolume`
  - `FSCTL_UNLOCK_VOLUME` -> `CdUnlockVolume`
  - `FSCTL_DISMOUNT_VOLUME` -> `CdDismountVolume`
  - `FSCTL_IS_VOLUME_DIRTY` -> `CdIsVolumeDirty`
  - `FSCTL_IS_VOLUME_MOUNTED` -> `CdIsVolumeMounted`
  - `FSCTL_IS_PATHNAME_VALID` -> `CdIsPathnameValid`
  - `FSCTL_INVALIDATE_VOLUMES` -> `CdInvalidateVolumes`
  - `FSCTL_ALLOW_EXTENDED_DASD_IO` -> `CdAllowExtendedDasdIo`

## Mount Path

`CdMountVolume` verifies media, reads drive geometry, determines block factor, acquires global CDFS synchronization, creates a volume device object, initializes overflow queues, processes the CD TOC, initializes the VCB, reads primary and supplementary volume descriptors, optionally allocates the sector cache, detects remounts, initializes VCB fields from the volume descriptor, queries SCSI transfer limits, releases residual references, marks the VCB mounted, sends mount notification, and completes the IRP.

ReactOS-specific branches allow disk-backed ISO mounting through `CdData.HddFileSystemDeviceObject`, using disk IOCTLs instead of CDROM IOCTLs where appropriate.

The mount path supports:
- Normal ISO/HSG/Joliet data discs.
- Audio disc fallback when no valid PVD is found but audio tracks exist and the data track is not first.
- Remounting a prior `VcbNotMounted` VCB by swapping VPB/device state.
- Single-track sector-cache allocation for directory acceleration.

## Verify Path

`CdVerifyVolume` reacquires the mounted VCB and checks whether media is still the same. It:

1. Runs `IOCTL_CDROM_CHECK_VERIFY`.
2. Uses media change count when available.
3. Re-reads and compares the TOC.
4. For data discs, finds the primary VD, optionally finds active Joliet VD, compares serial number, and compares volume label.
5. Marks the volume mounted and clears the verify bit if successful.
6. On wrong volume, marks the VCB not mounted, frees XA and directory cache state, and may trigger dismount if no user handles remain.
7. Sends remount notification when `VCB_STATE_NOTIFY_REMOUNT` is set.

## Volume Locking and Dismount

- `CdLockVolumeInternal`: purges the volume, waits for lazy writer activity, reacquires the VCB exclusively, runs delayed close processing, and succeeds only if cleanup/user-reference counts show no other user handles. It sets `VCB_STATE_LOCKED`, `VPB_LOCKED`, and records the locking file object.
- `CdUnlockVolumeInternal`: clears explicit lock state if the caller matches `VolumeLockFileObject`.
- `CdLockVolume`: accepts only `UserVolumeOpen`, sends lock notification, acquires the VCB exclusive, verifies it, calls the internal lock helper, and sends lock-failed notification on failure.
- `CdUnlockVolume`: accepts only `UserVolumeOpen`, calls the internal unlock helper, and sends unlock notification on success.
- `CdDismountVolume`: accepts only `UserVolumeOpen`, sends dismount notification, makes the request waitable, acquires global/Vcb synchronization, marks the VCB invalid and dismounted, sets `CCB_FLAG_DISMOUNT_ON_CLOSE`, and completes. On newer NTDDI it calls `FsRtlDismountComplete`.

## Oplocks

`CdOplockRequest` allows oplocks only on `UserFileOpen`. It forces a waitable IRP context, acquires the FCB exclusive for oplock requests or shared for break acknowledgements, verifies the FCB, calls `FsRtlOplockFsctrl`, updates `IsFastIoPossible`, releases the FCB, and lets the oplock package complete the IRP when appropriate.

For level 2 oplocks it checks current or in-progress byte-range locks; for other request oplocks it uses `FcbCleanup` as the open count.

## Miscellaneous FSCTLs

- `CdIsVolumeDirty`: validates a user volume open and output buffer, always reports clean state for mounted CDFS volumes.
- `CdIsVolumeMounted`: decodes the file object, disables popups, verifies the VCB if present, and returns success if no verification error is raised.
- `CdIsPathnameValid`: always succeeds.
- `CdAllowExtendedDasdIo`: accepts only user volume opens and sets `CCB_FLAG_ALLOW_EXTENDED_DASD_IO`.
- `CdInvalidateVolumes`: privileged operation requiring `SeTcbPrivilege`; obtains a file object from an input handle, finds all VCBs on the same real device, swaps VPB state if necessary, marks volumes invalid, purges, and checks for dismount.
- `CdScanForDismountedVcb`: opportunistically walks the global VCB queue and calls `CdCheckForDismount` on invalid, dismounting, or low-reference not-mounted volumes.

## Volume Descriptor Scanning

- `CdFindPrimaryVd`: scans for a primary volume descriptor. It may make two passes: first using last-session information for multisession discs, then from sector zero. It recognizes ISO and HSG standard IDs, rejects wrong versions/terminators, and records VCB volume type, base sector, VD sector offset, and primary VD offset when not in verify mode.
- `CdFindActiveVolDescriptor`: searches for a supported Joliet secondary descriptor unless `CdNoJoliet` is set. It accepts known Joliet escape sequences, switches VCB state from ISO to Joliet, records the active descriptor offset, computes serial number, and stores a trimmed Unicode volume label in the VPB. If no supplementary descriptor is found, it restores the saved primary descriptor.
- `CdIsRemount`: compares a new VCB against not-mounted VCBs on the same real device. Audio discs compare TOC contents; data discs compare serial number, TOC, and volume label.
- `CdReMountOldVcb`: moves the old VCB to the new target device/VPB, updates condition/media-change count, clears VPB-not-on-device state, and transfers sector-cache buffer ownership from the new VCB.

## Error Handling and Cleanup

The mount and verify paths use structured try/finally cleanup heavily. They free TOC and volume descriptor buffers, restore verify state on failed mounts, delete temporary device objects, dismount partially initialized VCBs, release global resources, and dereference notification file objects. Several status codes are deliberately normalized to `STATUS_WRONG_VOLUME` to allow RAW or other filesystem handling.

## Dependencies

This file depends on CDFS VCB lifecycle helpers, low-level device IOCTL helpers, TOC processing, cache purge/dismount helpers, VPB spin-lock manipulation, CDFS volume descriptor macros, name endian conversion, notification APIs, oplock APIs, privilege checks, and ReactOS-specific filesystem-device branching.

## Research Notes

`fsctrl.c` is the central lifecycle file for CDFS volumes. Its most important invariants are global mount/verify serialization, VCB exclusive ownership during state transitions, careful VPB manipulation under spin lock, and consistency checks between TOC, serial number, and volume label during verify/remount.
