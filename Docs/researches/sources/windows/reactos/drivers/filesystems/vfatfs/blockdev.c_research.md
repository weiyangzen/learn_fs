# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/blockdev.c

This file implements VFAT low-level block-device read, write, partial-MDL I/O, and IOCTL helpers.

Key functions:
- `VfatReadWritePartialCompletion`
  - Completion routine for partial read/write IRPs.
  - Frees the IRP’s MDL chain, propagates failure status to the original IRP, tracks pending-returned state, decrements `IrpContext->RefCount`, signals the context event when the last pending partial completes, frees the partial IRP, and returns `STATUS_MORE_PROCESSING_REQUIRED`.
- `VfatReadDisk`
  - Builds a synchronous `IRP_MJ_READ` with `IoBuildSynchronousFsdRequest`.
  - Optionally sets `SL_OVERRIDE_VERIFY_VOLUME`.
  - Waits on pending I/O and retries after successful `IoVerifyVolume` on `STATUS_VERIFY_REQUIRED`.
- `VfatReadDiskPartial`
  - Builds an asynchronous read IRP against `DeviceExt->StorageDevice`.
  - Creates a partial MDL from the original request’s MDL at `BufferOffset`.
  - Installs the shared completion routine.
  - Either waits for completion or increments the context reference count for async aggregation.
  - Retries after successful volume verification.
- `VfatWriteDisk`
  - Synchronous write counterpart to `VfatReadDisk`, including optional verify override and retry after media verification.
- `VfatWriteDiskPartial`
  - Partial-MDL asynchronous write counterpart to `VfatReadDiskPartial`.
- `VfatBlockDeviceIoControl`
  - Builds synchronous device I/O control requests, optionally overrides verify, waits on pending I/O, retries after volume verification, and returns output length through `OutputBufferSize`.

Notable design points:
- Media-change handling is centralized in every block helper: on `STATUS_VERIFY_REQUIRED`, the code obtains the thread’s verify device, clears it, calls `IoVerifyVolume`, and reissues the original request on success.
- Partial I/O uses independent child IRPs and MDLs but reports final failure back through the parent IRP context.
- The write partial setup assigns length/offset through `Parameters.Read`, relying on the read/write union layout.
