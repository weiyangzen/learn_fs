# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/CdoStruct.h

## Purpose

Defines global state, flag values, CDO identity helpers, and debug tracing macros for the CDO minifilter sample.

## Data Structures

- `CDO_GLOBAL_DATA` stores:
  - Filter Manager handle.
  - Driver object pointer.
  - Control device object pointer.
  - CDO open-state flags.
  - `ERESOURCE` protecting flag access.
  - Debug level in DBG builds.
- Declares `extern CDO_GLOBAL_DATA Globals`.

## Constants And Macros

- `GLOBAL_DATA_F_CDO_OPEN_REF` tracks an outstanding object reference to the CDO.
- `GLOBAL_DATA_F_CDO_OPEN_HANDLE` tracks an outstanding user handle to the CDO.
- `CONTROL_DEVICE_OBJECT_NAME` is `\FileSystem\Filters\CdoSample`.
- `IS_MY_CONTROL_DEVICE_OBJECT()` verifies the device object matches `Globals.FilterControlDeviceObject` and asserts driver object/device extension invariants.
- DBG-only trace flags distinguish errors, load/unload, CDO create/delete, supported operations, Fast I/O operations, all operations, and all flags.

## Dependencies

- Requires WDK types from `fltKernel.h` via `pch.h`.
- Used by both `CdoInit.c` and `CdoOperations.c`.

## Risks And Invariants

- Open reference and open handle are intentionally separate because cleanup and close are separate IRP phases.
- `IS_MY_CONTROL_DEVICE_OBJECT()` assumes `Globals.FilterControlDeviceObject` is initialized before dispatch paths use it.
- In free builds `DebugTrace` compiles to no-op.
