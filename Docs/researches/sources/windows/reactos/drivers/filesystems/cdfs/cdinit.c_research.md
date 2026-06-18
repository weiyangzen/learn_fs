# File Research: sources/windows/reactos/drivers/filesystems/cdfs/cdinit.c

## Purpose

`cdinit.c` implements driver initialization, unload, and global data setup for the ReactOS CDFS driver.

## Key Contents

- `DriverEntry`
  - Creates the primary filesystem device object named `\Cdfs` with type `FILE_DEVICE_CD_ROM_FILE_SYSTEM`.
  - ReactOS additionally creates `\CdfsHdd` with type `FILE_DEVICE_DISK_FILE_SYSTEM`.
  - Installs `CdUnload`.
  - Sets all supported `MajorFunction` entries to `CdFsdDispatch`.
  - Assigns `DriverObject->FastIoDispatch = &CdFastIoDispatch`.
  - Registers filesystem filter callbacks, currently `CdFilterCallbackAcquireForCreateSection`.
  - Calls `CdInitializeGlobalData`.
  - Marks filesystem device objects with `DO_LOW_PRIORITY_FILESYSTEM`.
  - Registers the filesystem device object(s) with `IoRegisterFileSystem`.
  - References registered device objects to keep them alive.
  - Optionally initializes telemetry.

- `CdUnload`
  - Frees cached IRP contexts from `CdData.IrpContextList`.
  - Frees `CdData.CloseItem`.
  - Deletes `CdData.DataResource`.
  - Dereferences filesystem device object(s).

- `CdInitializeGlobalData`
  - Zeros and initializes `CdFastIoDispatch`.
  - Hooks fast-I/O routines:
    - `CdFastIoCheckIfPossible`
    - `FsRtlCopyRead`
    - fast query info routines
    - fast lock/unlock routines
    - network open info
    - MDL read/write helpers
  - Initializes `CdData` node type, driver/device pointers, VCB queue, global resource, cache-manager callbacks, close queues, and mutex.
  - Allocates `CdData.CloseItem`.
  - Sets IRP-context cache depth and delayed-close thresholds based on `MmQuerySystemSize`.

## Dependencies and Interactions

- Uses `CdFsdDispatch` from `cddata.c`.
- Populates the `CdData` structure defined in `cdstruc.h`.
- Initializes delayed/async close infrastructure consumed by `close.c`.
- Cache callbacks point to routines declared in `cdprocs.h`.
- ReactOS-specific dual filesystem registration lets the same CDFS code participate for both CD-ROM and disk-style filesystem device types.

## Behavioral Notes

- Device object flags deliberately do not set direct or buffered I/O because CDFS chooses caching/direct I/O behavior per operation.
- Failure paths delete already-created device objects and abort initialization.
- `CdInitializeGlobalData` may fail only after `CloseItem` allocation failure in this file, returning `STATUS_INSUFFICIENT_RESOURCES`.
