# File Research: sources/windows/windows-driver-samples/filesys/cdfs/fsctrl.c

## Purpose

Implements CDFS filesystem-control handling: mount, verify, user FSCTLs, oplocks, volume lock/unlock/dismount, dirty/mounted/path queries, volume invalidation, extended DASD reads, stale VCB cleanup, remount detection, and primary/Joliet volume descriptor scanning.

## Main Entry Points

- `CdCommonFsControl`
- `CdUserFsctl`
- `CdMountVolume`
- `CdVerifyVolume`
- `CdOplockRequest`
- `CdLockVolume`
- `CdUnlockVolume`
- `CdDismountVolume`
- `CdIsVolumeDirty`
- `CdIsVolumeMounted`
- `CdIsPathnameValid`
- `CdInvalidateVolumes`
- `CdAllowExtendedDasdIo`
- `CdScanForDismountedVcb`
- `CdFindPrimaryVd`
- `CdIsRemount`
- `CdFindActiveVolDescriptor`

Global toggles:

- `CdDisable`: disables mounting.
- `CdNoJoliet`: disables Joliet secondary volume descriptor selection.

## Dispatch and User FSCTLs

`CdCommonFsControl` handles `IRP_MN_USER_FS_REQUEST`, `IRP_MN_MOUNT_VOLUME`, and `IRP_MN_VERIFY_VOLUME`. Other minor functions complete with `STATUS_INVALID_DEVICE_REQUEST`.

`CdUserFsctl` dispatches these user controls:

- oplock request/ack controls
- `FSCTL_LOCK_VOLUME`
- `FSCTL_UNLOCK_VOLUME`
- `FSCTL_DISMOUNT_VOLUME`
- `FSCTL_IS_VOLUME_DIRTY`
- `FSCTL_IS_VOLUME_MOUNTED`
- `FSCTL_IS_PATHNAME_VALID`
- `FSCTL_INVALIDATE_VOLUMES`
- `FSCTL_ALLOW_EXTENDED_DASD_IO`

Unknown controls return `STATUS_INVALID_DEVICE_REQUEST`.

## Mount Path

`CdMountVolume` expects a CD-ROM real device and a waitable IRP context. It updates `IrpContext->RealDevice`, honors `CdDisable` and shutdown state, performs `IOCTL_CDROM_CHECK_VERIFY` to collect media change count, optionally queries drive geometry to determine block factor, acquires global CDFS data, scans for removable stale VCBs, creates a volume device object, initializes overflow queue state, reads the TOC, and initializes a new VCB.

For data discs it allocates a sector-sized descriptor buffer and calls `CdFindPrimaryVd`. If no valid PVD is found but the TOC indicates suitable audio content, it may mount as an audio/CD-XA disk. When a PVD is found, it preserves it, then calls `CdFindActiveVolDescriptor` to select a supported Joliet secondary descriptor when present.

It allocates a directory sector cache only for non-audio single-track media. It then checks `CdIsRemount`; on remount, it transfers the new device object and sector cache to the old VCB through `CdReMountOldVcb` and may issue mount notification if the old VCB requested it. New mounts call `CdUpdateVcbFromVolDescriptor`, capture SCSI transfer limits, drop residual references, dereference the target device object, mark the VCB mounted, and send mount notification.

Failure cleanup is extensive: unowned TOC and descriptor buffers are freed, verify is restored when appropriate, partially installed VPBs are detached, incomplete VCBs are dismounted, leftover device objects are deleted, and the global resource is released.

## Verify Path

`CdVerifyVolume` reacquires global state and the VCB exclusively, rejects invalid/dismounting VCBs, performs check-verify, compares media change count, rereads and compares TOC when needed, and for data discs rereads descriptors. It reselects the active descriptor, compares serial number and volume label against the VPB, and returns `STATUS_WRONG_VOLUME` on mismatch.

On success it marks the VCB mounted and clears the real-device verify bit. On wrong volume it marks the VCB not mounted, frees XA and directory cache state, may purge the volume, and checks for dismount if no cleanup handles remain. It updates media change count regardless of outcome.

## Volume Locking and Dismount

`CdLockVolumeInternal` purges the volume, waits for lazy writer activity, forces waitable reacquire of the VCB, drains FSP closes, and sets `VCB_STATE_LOCKED` plus `VPB_LOCKED` only if user references match the allowed residual counts. Explicit locks record the locking file object.

`CdUnlockVolumeInternal` clears `VCB_STATE_LOCKED`, `VPB_LOCKED`, and `VolumeLockFileObject` only when the unlock caller matches the recorded lock file object.

`CdLockVolume` accepts only `UserVolumeOpen`, sends `FSRTL_VOLUME_LOCK`, acquires the VCB exclusive, verifies it, calls the internal lock helper, and sends lock-failed notification on failure.

`CdUnlockVolume` accepts only `UserVolumeOpen`, calls the internal unlock helper, and sends `FSRTL_VOLUME_UNLOCK` on success.

`CdDismountVolume` accepts only `UserVolumeOpen`, sends `FSRTL_VOLUME_DISMOUNT`, acquires global data and VCB exclusive, invalidates mounted volumes, sets `VCB_STATE_DISMOUNTED`, marks the CCB with `CCB_FLAG_DISMOUNT_ON_CLOSE`, and calls `FsRtlDismountComplete` on Windows 8+.

## Other User Controls

`CdOplockRequest` allows oplocks only on `UserFileOpen`. It makes the IRP context waitable, acquires the FCB exclusive for new oplock requests or shared for break acknowledgements, verifies the FCB, calls `FsRtlOplockFsctrl`, updates `IsFastIoPossible`, and lets the oplock package complete the IRP.

`CdIsVolumeDirty` requires a system output buffer large enough for `ULONG`, accepts only `UserVolumeOpen`, rejects dismounted volumes, and always returns a clean state because CDFS is read-only.

`CdIsVolumeMounted` decodes the file object, verifies the VCB if an FCB is available, and otherwise succeeds.

`CdIsPathnameValid` always succeeds.

`CdAllowExtendedDasdIo` accepts only `UserVolumeOpen` and sets `CCB_FLAG_ALLOW_EXTENDED_DASD_IO`.

`CdInvalidateVolumes` is restricted to the filesystem device object and requires `SeTcbPrivilege`. It accepts a file-object handle, extracts the underlying device object, walks all VCBs for that real device, swaps VPBs off the device when needed, marks matching volumes invalid, purges them, and checks for dismount.

`CdScanForDismountedVcb` walks the global VCB queue and calls `CdCheckForDismount` on VCBs already dismounting, invalid, or not mounted with only residual references.

## Descriptor and Remount Helpers

`CdFindPrimaryVd` searches at most two passes: first using last-session/multisession information when available, then from sector zero. It skips audio-only VCBs, reads descriptors starting at `FIRST_VD_SECTOR`, recognizes ISO and HSG identifiers, rejects invalid versions and terminators, and records VCB volume type, base sector, current descriptor offset, and primary descriptor offset when not in verify mode.

`CdIsRemount` scans existing VCBs on the same real device in `VcbNotMounted` state. Audio disks match by TOC. Data disks match by serial number, TOC, volume label length/content, and real device.

`CdFindActiveVolDescriptor` scans ISO descriptors for supported Joliet secondary descriptors unless `CdNoJoliet` is set. It recognizes the supported Joliet escape sequences, updates VCB state and descriptor offset when not verifying, restores the saved PVD if no secondary descriptor is selected, and on mount computes the VPB serial number and Unicode volume label with trailing spaces/nulls stripped.

## Dependencies

This file coordinates most global CDFS state and uses VPB spin locks, CDFS VCB/FCB resources, TOC processing, low-level device I/O controls, sector reads, descriptor macros, purge/dismount helpers, FsRtl volume notifications, oplock helpers, and optional telemetry.
