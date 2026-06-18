# File Research: sources/windows/reactos/drivers/filesystems/fastfat/devctrl.c

This file implements FastFAT `IRP_MJ_DEVICE_CONTROL` handling. It accepts device-control requests only on user volume opens, performs limited filesystem-side policy for snapshot, disk-copy, and SCSI pass-through IOCTLs, and otherwise forwards requests to the lower storage device.

Key responsibilities:
- Dispatch device-control IRPs through `FatFsdDeviceControl`.
- Validate that the file object decodes as `UserVolumeOpen`.
- Intercept `IOCTL_VOLSNAP_FLUSH_AND_HOLD_WRITES` to flush the FAT volume and hold file resources while the lower driver processes the request.
- Deny `IOCTL_DISK_COPY_DATA` unless the volume is locked, forced direct write is requested, or the handle completed a dismount.
- Detect SCSI `FORMAT_UNIT` pass-through commands and mark the CCB/file object so close-time verification can occur.
- Forward all accepted IOCTLs to `Vcb->TargetDeviceObject`.

Important functions:
- `FatFsdDeviceControl`: FSD wrapper that enters the filesystem, establishes top-level IRP state, creates an IRP context with waitability from `CanFsdWait`, calls `FatCommonDeviceControl`, and routes exceptions through `FatProcessException`.
- `FatCommonDeviceControl`: Main IOCTL handler. It decodes the user volume open, switches on `IoControlCode`, performs special handling for snapshot flush/hold, direct disk copy, and SCSI pass-through format commands, forwards the IRP to the target device, and completes or detaches the IRP as appropriate.
- `FatDeviceControlCompletionRoutine`: Completion routine used by the synchronous snapshot path; signals an event and returns `STATUS_MORE_PROCESSING_REQUIRED` when an event context is supplied.

Important interactions:
- Uses `FatDecodeFileObject` to reject file/directory opens for device-control requests.
- Uses `FatAcquireExclusiveVolume`, `FatFlushAndCleanVolume`, and `FatReleaseVolume` for `IOCTL_VOLSNAP_FLUSH_AND_HOLD_WRITES`.
- Copies the current IRP stack location and installs a completion routine only for the snapshot hold path; most IOCTLs use `IoSkipCurrentIrpStackLocation`.
- Forwards accepted IOCTLs with `IoCallDriver(Vcb->TargetDeviceObject, Irp)`.
- Checks `VCB_STATE_FLAG_LOCKED`, `SL_FORCE_DIRECT_WRITE`, and `CCB_FLAG_COMPLETE_DISMOUNT` before allowing `IOCTL_DISK_COPY_DATA`.
- Parses `SCSI_PASS_THROUGH`, `SCSI_PASS_THROUGH_DIRECT`, `SCSI_PASS_THROUGH_EX`, and `SCSI_PASS_THROUGH_DIRECT_EX` buffers, including Wow64 32-bit structure variants when enabled.

Notable behavior and risks:
- The snapshot flush-and-hold path forces wait semantics, holds the volume exclusively, waits for lower-driver completion when pending, then releases the volume and completes the IRP itself.
- Non-snapshot forwarded IOCTLs set `Irp = NULL` before `FatCompleteRequest`, so completion belongs to the lower driver while the IRP context is still freed.
- SCSI format-unit detection is best-effort and only runs when the system buffer is present and the input buffer is large enough for the relevant pass-through structure.
- Only user volume opens can issue these device controls; other open types fail with `STATUS_INVALID_PARAMETER`.
