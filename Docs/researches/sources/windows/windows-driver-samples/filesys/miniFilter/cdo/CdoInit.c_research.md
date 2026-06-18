# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/CdoInit.c

## Purpose

Initializes the control device object minifilter sample. It registers a minifilter for lifetime management, creates a named control device object, initializes global synchronization, optionally reads debug settings, and deliberately refuses volume attachment.

## Public And Internal APIs

- Driver lifecycle: `DriverEntry()`, `CdoUnload()`.
- Instance callback: `CdoInstanceSetup()`.
- Debug-only registry helpers: `CdoGetIoOpenDriverRegistryKey()`, `CdoOpenServiceParametersKey()`, `CdoInitializeDebugLevel()`.

## Control Flow

- `DriverEntry()` zeroes `Globals`, initializes debug level in DBG builds, initializes `Globals.Resource`, records the driver object, registers a minimal `FLT_REGISTRATION`, creates the control device object through `CdoCreateControlDeviceObject()`, and starts filtering.
- Failure after each stage unwinds the prior stage: unregisters the filter, deletes the resource, and/or deletes the CDO.
- `CdoUnload()` refuses optional unload when the CDO still has an open reference, unregisters the minifilter, deletes the CDO, releases the resource, and deletes the resource object.
- `CdoInstanceSetup()` returns `STATUS_FLT_DO_NOT_ATTACH`, so the minifilter does not attach to any volume; this sample focuses on the CDO surface rather than file I/O filtering.

## Registration

- `FLT_REGISTRATION` has no contexts and no operation callbacks.
- It supplies unload and instance setup callbacks only.
- KTM/name-provider callbacks are unused.

## State And Data Structures

- Uses the global `CDO_GLOBAL_DATA Globals` declared in `CdoStruct.h`.
- `Globals.Resource` serializes CDO open/close/unload state.
- `Globals.FilterDriverObject`, `Globals.Filter`, and `Globals.FilterControlDeviceObject` are initialized across driver entry and CDO creation.

## Dependencies

- Filter Manager lifecycle APIs: `FltRegisterFilter`, `FltStartFiltering`, `FltUnregisterFilter`.
- Kernel resource APIs: `ExInitializeResourceLite`, `ExDeleteResourceLite`.
- Debug-only registry reads use `IoOpenDriverRegistryKey` when available, otherwise `ZwOpenKey` on the service `Parameters` subkey, then `ZwQueryValueKey("DebugLevel")`.

## Risks And Invariants

- Optional unload is blocked while `GLOBAL_DATA_F_CDO_OPEN_REF` is set; mandatory unload proceeds.
- The resource must remain valid until CDO state is no longer inspected.
- The sample’s filter instance callbacks exist mainly to make a loadable minifilter package while demonstrating a separately named device object.
