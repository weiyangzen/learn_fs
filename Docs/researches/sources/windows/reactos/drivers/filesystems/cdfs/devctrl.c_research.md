# File Research: sources/windows/reactos/drivers/filesystems/cdfs/devctrl.c

## Purpose
Implements CDFS device-control dispatch for user volume handles, forwarding most CD-ROM IOCTLs to the lower storage stack while handling disk-type reporting directly.

## Key Elements
- `CdCommonDevControl` decodes the file object and accepts only `UserVolumeOpen` handles.
- `IOCTL_CDROM_READ_TOC` causes a VCB verify before forwarding, so media changes are detected.
- `IOCTL_CDROM_DISK_TYPE` is handled inside CDFS: it verifies the VCB, checks for a `CDROM_DISK_DATA`-sized output buffer, copies `Vcb->DiskFlags` into the system buffer, sets the information length, and completes successfully.
- Other accepted device controls are forwarded by copying the current stack location to the next stack location, installing `CdDevCtrlCompletionRoutine`, calling the target device object, and completing only the CDFS IRP context.
- `CdDevCtrlCompletionRoutine` propagates pending state by calling `IoMarkIrpPending` when `PendingReturned` is set.

## Dependencies
Uses CDFS file-object decoding and VCB verification helpers, the lower `TargetDeviceObject`, Windows CD-ROM IOCTL definitions, and standard IRP stack/completion routines.

## Behavior/Risks
- Device controls through file or directory handles are rejected with `STATUS_INVALID_PARAMETER`.
- The direct `IOCTL_CDROM_DISK_TYPE` path relies on `Vcb->DiskFlags` having been populated during mount/recognition.
- Forwarded IOCTLs preserve the caller's stack parameters and depend on the lower CD-ROM/storage driver for final completion.
- The completion routine intentionally returns `STATUS_SUCCESS`, so forwarded IRPs continue normal I/O manager completion after pending state is fixed up.
