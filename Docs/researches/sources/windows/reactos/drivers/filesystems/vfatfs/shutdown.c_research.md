# File Research: sources/windows/reactos/drivers/filesystems/vfatfs/shutdown.c

## Purpose

`shutdown.c` handles `IRP_MJ_SHUTDOWN` for the VFAT filesystem. It flushes all mounted volumes, clears dirty bits for clean shutdown where appropriate, passes shutdown to the lower storage device, and optionally checks for dismount.

## Main Flow

- `VfatDiskShutDown()` builds a synchronous `IRP_MJ_SHUTDOWN` request for the lower storage device, calls the driver, waits if pending, and returns the final status.
- `VfatShutdown()`:
  - Enters filesystem context.
  - Sets `VfatGlobalData->ShutdownStarted`.
  - Accepts shutdown only on the global filesystem device object.
  - Acquires the global volume-list lock.
  - For each mounted VCB:
    - acquires `DirResource`
    - flushes volume/files through `VfatFlushVolume()`
    - clears the on-disk dirty bit if `VCB_CLEAR_DIRTY` and `VCB_IS_DIRTY` are both set and `SetDirtyStatus(FALSE)` succeeds
    - sends shutdown to the storage device
    - releases `DirResource`
    - under `ENABLE_SWAPOUT`, calls `VfatCheckForDismount(DeviceExt, FALSE)`
  - Completes the original IRP.

## Important Details

- There is a FIXME noting that new mount requests should be blocked during shutdown.
- The code preserves the first failure by storing failed statuses in the shutdown IRP status as it iterates volumes.
- The global resource cleanup is also marked FIXME.

## Research Notes

This file ties into dirty-bit semantics established during mount and lock/dismount. Clean shutdown depends on the volume having been marked with `VCB_CLEAR_DIRTY` during mount or lock-time cleanup.
