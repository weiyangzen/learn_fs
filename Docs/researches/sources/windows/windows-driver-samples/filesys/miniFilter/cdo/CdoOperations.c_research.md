# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/CdoOperations.c

## Purpose

Implements creation, deletion, IRP dispatch, open/cleanup/close state management, FS-control handling, and Fast I/O dispatch behavior for the CDO sample’s named control device object.

## Public And Internal APIs

- CDO lifecycle: `CdoCreateControlDeviceObject()`, `CdoDeleteControlDeviceObject()`.
- IRP dispatch: `CdoMajorFunction()`.
- Supported private operations: `CdoHandlePrivateOpen()`, `CdoHandlePrivateCleanup()`, `CdoHandlePrivateClose()`, `CdoHandlePrivateFsControl()`.
- Fast I/O dispatch table: `CdoFastIoDispatch`.
- Fast I/O callbacks cover check/read/write/query info/locks/device control/network open/MDL/compressed/query-open operations.

## Control Flow

- `CdoCreateControlDeviceObject()` creates `\FileSystem\Filters\CdoSample` with `FILE_DEVICE_DISK_FILE_SYSTEM` and `FILE_DEVICE_SECURE_OPEN`, installs `CdoMajorFunction` for every IRP major code, and installs `CdoFastIoDispatch`.
- `CdoDeleteControlDeviceObject()` calls `IoDeleteDevice()` on `Globals.FilterControlDeviceObject`.
- `CdoMajorFunction()` asserts the device object is the sample CDO, then supports:
  - `IRP_MJ_CREATE`: calls `CdoHandlePrivateOpen()`, completes with `FILE_OPENED` on success.
  - `IRP_MJ_CLOSE`: calls `CdoHandlePrivateClose()` and always completes success.
  - `IRP_MJ_FILE_SYSTEM_CONTROL`: forwards system buffer and lengths to `CdoHandlePrivateFsControl()`.
  - `IRP_MJ_CLEANUP`: calls `CdoHandlePrivateCleanup()` and always completes success.
  - All other major codes complete with `STATUS_INVALID_DEVICE_REQUEST`.
- `CdoHandlePrivateOpen()` takes the global resource exclusive and permits only one outstanding open at a time. It sets both `GLOBAL_DATA_F_CDO_OPEN_REF` and `GLOBAL_DATA_F_CDO_OPEN_HANDLE` on success.
- `CdoHandlePrivateCleanup()` clears `GLOBAL_DATA_F_CDO_OPEN_HANDLE`; `CdoHandlePrivateClose()` later clears `GLOBAL_DATA_F_CDO_OPEN_REF`.
- `CdoHandlePrivateFsControl()` takes the resource shared, asserts an open reference exists, fails if cleanup already closed the handle, then demonstrates two phases: work requiring the handle still be open while the resource is held, and work that can continue after the handle may close while the IRP’s device reference remains.

## Fast I/O Behavior

- Almost every Fast I/O callback asserts the CDO and returns a terminal failure for the CDO, usually by setting `IoStatus->Status = STATUS_INVALID_DEVICE_REQUEST`, `Information = 0`, and returning `TRUE`.
- MDL completion routines return `FALSE` because there is no operation to complete.
- `CdoFastIoDeviceControl()` is the main exception: it routes the Fast I/O device-control request into `CdoHandlePrivateFsControl()` and returns `TRUE`.
- `CdoFastIoQueryOpen()` writes failure status into the create IRP’s `IoStatus` and returns `TRUE`.

## State And Data Structures

- Global open state is represented by `Globals.Flags`:
  - `GLOBAL_DATA_F_CDO_OPEN_REF` means the CDO still has an object reference and close has not run.
  - `GLOBAL_DATA_F_CDO_OPEN_HANDLE` means a user handle remains open and cleanup has not run.
- `Globals.Resource` protects flag transitions and unload checks.
- Driver dispatch table and Fast I/O table are installed on the shared driver object during CDO creation.

## Dependencies

- Kernel APIs: `IoCreateDevice`, `IoDeleteDevice`, `IoGetCurrentIrpStackLocation`, `IoCompleteRequest`.
- Synchronization wrappers from `CdoProc.h`: `CdoAcquireResourceExclusive`, `CdoAcquireResourceShared`, `CdoReleaseResource`.
- Debug and identity macros from `CdoStruct.h`: `DebugTrace`, `IS_MY_CONTROL_DEVICE_OBJECT`.

## Risks And Invariants

- The sample enforces one open handle to the CDO. Create fails with `STATUS_DEVICE_ALREADY_ATTACHED` if either open flag is already set.
- Cleanup and close ordering matters: cleanup clears the handle flag, close clears the reference flag. Assertions encode the expected IRP sequence.
- FS-control must check `GLOBAL_DATA_F_CDO_OPEN_HANDLE` while holding the resource if the requested operation requires the user handle still to be open.
- After releasing the resource in FS-control, cleanup may run; only operations independent of the live handle are safe in that phase.
- The Fast I/O table is intentionally broad so unexpected fast paths are handled explicitly rather than falling through to undefined behavior.
