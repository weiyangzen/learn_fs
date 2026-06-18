# File Research: sources/windows/reactos/drivers/filesystems/udfs/verfysup.cpp

This file implements UDF volume verification, media-change handling, quick remount support, dismount checks, VCB teardown, and old/new VCB comparison.

Key functions:
- `UDFVerifyVcb`
  - Rejects VCBs being dismounted.
  - For removable media, sends `IOCTL_STORAGE_CHECK_VERIFY` unless media is locked and no unsafe IOCTL was seen.
  - Sets `DO_VERIFY_VOLUME` when media-change count changes, raw/no-media states appear, or unsafe IOCTL state forces verification.
  - Raises `STATUS_VERIFY_REQUIRED`, `STATUS_WRONG_VOLUME`, or `STATUS_FILE_INVALID` through the IRP context as needed.
- `UDFVerifyVolume`
  - Handles `IRP_MN_VERIFY_VOLUME`.
  - Checks media, allocates a temporary `NewVcb`, reads disk info, initializes read-only write-cache state, and compares physical then logical media identity.
  - Supports raw-disk handling, mount-error thresholds, and quick-remount cache reinitialization.
  - Clears `DO_VERIFY_VOLUME` on successful verification and restarts eject waiter/cache state if the old VCB remains mounted.
  - Cleans temporary VCB/cache state before returning and completes the verify IRP.
- `UDFPerformVerify`
  - Called from exception handling when a request encountered `STATUS_VERIFY_REQUIRED`.
  - Avoids recursive verify during mount/verify FSCTLs.
  - Calls `IoVerifyVolume`, normalizes wrong-volume cases when the VCB is already mounted, can dismount unreferenced VCBs, reparses absolute creates after remount, and posts the original request on success.
- `UDFCheckForDismount`
  - Tests open/reference counts under global and VCB resources.
  - Starts dismount when only residual filesystem references remain.
  - Releases the VCB when teardown is underway and VPB references drain.
- `UDFDismountVcb`
  - Marks the VCB as being dismounted.
  - Allocates a replacement VPB when needed.
  - Closes residual references, swaps or clears VPB state under the VPB spinlock, stops eject waiter, and releases the VCB on final reference.
- `UDFCompareVcb`
  - Physical comparison checks media LBA ranges, track numbers, NWA, possible last LBA, physical serial/type/erasable state, media class, target device object, last session, and per-track ranges/parameters.
  - Logical comparison checks VAT count, volume creation time, serial number, volume identifier, and root file identity.
  - Uses a simplified logical check if the old volume is modified, avoiding root directory inspection.

Notable design points:
- Verification is two-phase: physical identity first, logical UDF identity second.
- Temporary VCB/cache state is used to inspect current media without mutating the mounted VCB until identity is confirmed.
- Raw/blank media and bad-volume cases are explicitly handled.
- Dismount code carefully coordinates VCB resources, VPB spinlock state, residual references, and eject waiter shutdown.
