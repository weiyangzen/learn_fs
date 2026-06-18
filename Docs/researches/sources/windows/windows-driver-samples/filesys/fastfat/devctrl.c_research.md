# File Research: sources/windows/windows-driver-samples/filesys/fastfat/devctrl.c

## Purpose
Implements FastFAT `IRP_MJ_DEVICE_CONTROL` dispatch. The file mostly passes device IOCTLs down to the underlying target device, but interposes for volume snapshot flush/hold, direct-write safety, and SCSI format-unit tracking.

## Main Entry Points
- `FatFsdDeviceControl`: standard dispatch wrapper. It enters filesystem context, establishes top-level IRP state, creates an IRP context with wait capability based on `CanFsdWait`, calls `FatCommonDeviceControl`, and exception-processes failures.
- `FatCommonDeviceControl`: validates that the file object is a `UserVolumeOpen`, handles special IOCTLs, forwards the IRP to `Vcb->TargetDeviceObject`, and completes local context when needed.
- `FatDeviceControlCompletionRoutine`: completion routine used for synchronous wait cases; signals a caller-provided event and returns `STATUS_MORE_PROCESSING_REQUIRED`.

## IOCTL Behavior
- `IOCTL_VOLSNAP_FLUSH_AND_HOLD_WRITES`: sets wait mode, acquires the volume exclusively, flushes and cleans without purge, copies the stack to the next driver, installs `FatDeviceControlCompletionRoutine`, calls the lower driver, waits for completion if pending, then releases the held volume resources before completing the IRP.
- `IOCTL_DISK_COPY_DATA`: denied unless the FAT volume is locked, the caller supplied `SL_FORCE_DIRECT_WRITE`, or the CCB indicates a complete dismount. This prevents raw direct writes underneath a mounted filesystem.
- SCSI pass-through variants: inspects the CDB for `SCSIOP_FORMAT_UNIT`. If detected, marks the CCB with `CCB_FLAG_SENT_FORMAT_UNIT` and the file object with `FO_FILE_MODIFIED`, so later close/verify paths know media contents may have changed.
- Default path: skips the current stack location and forwards the request without a FAT completion routine.

## WOW64 Handling
For SCSI pass-through IOCTLs on 64-bit builds with WOW64 support, the code reads either 32-bit or native pass-through structures before extracting the CDB. It covers both classic and extended direct/non-direct SCSI pass-through layouts.

## Integration Points
- Requires device controls to arrive through a volume open, not arbitrary file/directory opens.
- Uses `FatAcquireExclusiveVolume`, `FatFlushAndCleanVolume`, and `FatReleaseVolume` for snapshot consistency.
- Uses CCB state to enforce direct-write and media-format side effects.
- Uses lower-device forwarding through `IoCallDriver`, with local completion only for the flush-and-hold case.

## Research Notes
This file is intentionally small compared with create handling. Its key filesystem responsibility is preserving mounted-volume correctness when callers send powerful device IOCTLs that can bypass normal FAT metadata paths.
