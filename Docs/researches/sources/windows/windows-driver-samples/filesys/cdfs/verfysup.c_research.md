# File Research: sources/windows/windows-driver-samples/filesys/cdfs/verfysup.c

## Purpose

Implements volume verification, FCB operation verification, dismount checks, and VCB dismount mechanics for CDFS.

## Main Entry Points

- `CdPerformVerify`
- `CdCheckForDismount`
- `CdMarkDevForVerifyIfVcbMounted`
- `CdVerifyVcb`
- `CdVerifyFcbOperation`
- `CdDismountVcb`

## Verification

`CdPerformVerify` handles `STATUS_VERIFY_REQUIRED` recovery. It avoids recursive verification for mount/verify FSCTLs, calls `IoVerifyVolume`, reconciles the result with current `VcbCondition`, triggers dismount when the old VCB is no longer valid and only residual references remain, reparses top-level creates after successful remount/wrong-volume outcomes, raises user-induced errors for hard-error UI, and posts the original request back to the FSP when verification succeeds.

`CdVerifyVcb` validates volume state before operations. On removable media, it checks `IOCTL_CDROM_CHECK_VERIFY`, compares media change count, detects raw/empty device outcomes, marks the real device for verify when still mounted, and forces root creates on unmounted/dismounting volumes through the verify path. It raises `STATUS_VERIFY_REQUIRED`, `STATUS_WRONG_VOLUME`, `STATUS_FILE_INVALID`, or `STATUS_VOLUME_DISMOUNTED` as appropriate.

`CdVerifyFcbOperation` is the per-file fast/common operation gate. It rejects most operations on cleaned-up file objects, fails invalid/dismounting volumes, raises verify-required when the real device is marked, allows mounted/mount-in-progress volumes, and raises wrong-volume for not-mounted VCBs in IRP paths. In fast-I/O calls it returns `FALSE` instead of raising.

## Dismount

`CdCheckForDismount` acquires the VCB exclusively, drains pending closes, starts dismount when user references are residual or force is requested, and deletes the VCB when dismount is already in progress and both VCB and VPB references allow it.

`CdDismountVcb` marks dismount in progress, frees XA sector state, removes internal FCB references, purges volume cache, drains close queues, drops the mount reference, and coordinates VPB replacement/deletion under the VPB spin lock. It may swap in the saved VPB so the real device can be remounted while the old VCB survives due to references.

`CdMarkDevForVerifyIfVcbMounted` safely marks the real device for verify only if the VCB’s VPB is still the active VPB for the device; otherwise it records that the VPB is no longer on the device.

## Dependencies

Uses CDFS global/VCB locks, VPB spin-lock protocol, device verify flags, mount/dismount state, close-queue draining, purge logic, IoVerifyVolume, and CDFS exception/posting helpers.
