# File Research: sources/windows/windows-driver-samples/filesys/cdfs/cdinit.c

## Purpose

`cdinit.c` implements CDFS driver initialization, unload, and global data setup.

## Main Routines

- `DriverEntry`
  - Creates the filesystem device object named `\Cdfs` with type `FILE_DEVICE_CD_ROM_FILE_SYSTEM`.
  - Installs `CdUnload`.
  - Assigns `CdFsdDispatch` to all supported major functions:
    - create, close, read, write, query/set file info, query volume info, directory control, FS control, device control, lock control, cleanup, PNP, shutdown.
  - Sets `DriverObject->FastIoDispatch` to `CdFastIoDispatch`.
  - Registers FS filter callback `CdFilterCallbackAcquireForCreateSection`.
  - Calls `CdInitializeGlobalData`.
  - Marks the filesystem as low priority with `DO_LOW_PRIORITY_FILESYSTEM`.
  - Registers with the I/O manager via `IoRegisterFileSystem`.
  - References the filesystem device object for global lifetime.
  - Optionally initializes telemetry.

- `CdUnload`
  - Frees cached IRP contexts from `CdData.IrpContextList`.
  - Frees the close work item.
  - Deletes `CdData.DataResource`.
  - Dereferences the filesystem device object.

- `CdInitializeGlobalData`
  - Initializes the `FAST_IO_DISPATCH` table.
  - Hooks fast query, lock/unlock, fast read, network info, and MDL operations.
  - Clears and initializes `CdData`.
  - Initializes VCB queue, `DataResource`, cache manager callbacks, volume cache no-op callbacks, mutexes, async/delayed close queues, and close work item.
  - Sizes IRP context and delayed close thresholds based on `MmQuerySystemSize`.

## Integration

This file wires the exported driver object to the rest of CDFS. The initialized `CdFastIoDispatch` and `CdData.CacheManagerCallbacks` are consumed by dispatch, cache, fast-I/O, and stream-file setup paths.

## Risk Notes

- Initialization failure unwinds the filesystem device object but must occur before registration.
- `CdUnload` assumes no active mounted volumes remain and only tears down global cached objects.
- Each registered IRP major function must match a case in `CdFsdDispatch`; the comments explicitly call out that invariant.
