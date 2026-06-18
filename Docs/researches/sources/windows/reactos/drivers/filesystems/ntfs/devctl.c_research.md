# File Research: sources/windows/reactos/drivers/filesystems/ntfs/devctl.c

Read status: complete file, 48 lines.

This file implements `IRP_MJ_DEVICE_CONTROL` passthrough.

Key entry point:
- `NtfsDeviceControl()` gets the mounted volume extension, skips the current IRP stack location, clears `IRPCONTEXT_COMPLETE` because the lower driver will complete the IRP, and forwards the IRP to `DeviceExt->StorageDevice`.

Important dependencies:
- Correct mount initialization of `DeviceExt->StorageDevice` in `fsctl.c`.
- Dispatch completion flags in `dispatch.c`.

Notable behavior:
- The NTFS driver does not inspect device-control codes here; all device-control IRPs are forwarded to the underlying storage stack.
- Completion ownership is explicitly transferred to the lower driver.
