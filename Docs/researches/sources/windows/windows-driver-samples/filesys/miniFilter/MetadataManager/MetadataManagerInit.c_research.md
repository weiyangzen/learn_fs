# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/MetadataManager/MetadataManagerInit.c

## Purpose

`MetadataManagerInit.c` is the initialization and lifecycle module for the MetadataManager minifilter sample.

It defines:

- Global filter state.
- Filter Manager operation registrations.
- Instance context registration.
- Driver entry and unload.
- Debug-level registry support for checked builds.
- Instance setup, teardown, and context cleanup.

## Global State

The file defines:

- `FMM_GLOBAL_DATA Globals`, which stores:
  - `PFLT_FILTER Filter`.
  - Debug level in checked builds.

It also defines unsupported device characteristics:

- `FILE_FLOPPY_DISKETTE`
- `FILE_READ_ONLY_DEVICE`
- `FILE_VIRTUAL_VOLUME`

The sample avoids attaching to those devices.

## Operation Registration

The `Callbacks` array registers the minifilter for:

- `IRP_MJ_CREATE`
- `IRP_MJ_CLEANUP`
- `IRP_MJ_FILE_SYSTEM_CONTROL`
- `IRP_MJ_DEVICE_CONTROL`
- `IRP_MJ_SHUTDOWN`
- `IRP_MJ_PNP`

Create registration depends on `VERIFY_METADATA_OPENED`:

- If verification is enabled, all non-paging creates are observed.
- Otherwise, non-DASD creates are skipped to avoid unnecessary overhead.

Cleanup and filesystem-control callbacks skip paging and non-DASD I/O. Device control, shutdown, and PnP skip paging I/O.

## Context Registration

The `ContextRegistration` array registers one context type:

- `FLT_INSTANCE_CONTEXT`
- Size: `FMM_INSTANCE_CONTEXT_SIZE`
- Cleanup callback: `FmmContextCleanup`
- Pool tag: `FMM_INSTANCE_CONTEXT_TAG`

The instance context stores per-volume metadata-file ownership and synchronization state.

## Filter Registration

`FilterRegistration` wires the filter to Filter Manager:

- Context registration.
- Operation callbacks.
- `FmmUnload`.
- `FmmInstanceSetup`.
- `FmmInstanceQueryTeardown`.
- `FmmInstanceTeardownStart`.
- `FmmInstanceTeardownComplete`.

Name provider callbacks are unused.

## `DriverEntry`

`DriverEntry` performs driver initialization:

- Opts into `NonPagedPoolNx` through `ExInitializeDriverRuntime`.
- Zeroes `Globals`.
- Initializes debug level in checked builds.
- Calls `FltRegisterFilter`.
- Calls `FltStartFiltering`.
- Unregisters the filter if start fails.
- Returns the final status.

## Debug Registry Helpers

Compiled only under `DBG`.

### `FmmGetIoOpenDriverRegistryKey`

Looks up `IoOpenDriverRegistryKey` dynamically with `MmGetSystemRoutineAddress`.

### `FmmOpenServiceParametersKey`

Opens the service parameters key:

- Preferably through `IoOpenDriverRegistryKey`.
- Falls back to opening the service root key and then `Parameters`.

### `FmmInitializeDebugLevel`

Reads `DebugLevel` from the service parameters key. Defaults to `DEBUG_TRACE_ERROR` when no registry value is found.

## `FmmUnload`

Unregisters the minifilter through `FltUnregisterFilter` and clears `Globals.Filter`.

It ignores unload flags and always returns `STATUS_SUCCESS`.

## `FmmContextCleanup`

Handles cleanup for registered contexts.

For `FLT_INSTANCE_CONTEXT`, it:

- Casts the context to `FMM_INSTANCE_CONTEXT`.
- Deletes `MetadataResource` with `ExDeleteResourceLite`.

Actual metadata handle/file-object closure is handled during instance teardown complete, not here.

## `FmmInstanceSetup`

`FmmInstanceSetup` decides whether the filter attaches to a volume and initializes per-instance state.

Attach criteria:

- Filesystem type must be NTFS, FAT, or ReFS.
- The underlying disk device must be `FILE_DEVICE_DISK`.
- The disk must not have unsupported characteristics such as floppy, read-only, or virtual volume.

Setup flow:

1. Validate filesystem type.
2. Get and inspect the disk device object.
3. Allocate an `FMM_INSTANCE_CONTEXT`.
4. Zero and initialize:
   - Flags.
   - Instance.
   - Filesystem type.
   - Volume.
   - Metadata resource.
5. Associate the context with the instance using `FltSetInstanceContext`.
6. Acquire the metadata resource exclusive.
7. Open metadata using `FmmOpenMetadata`.
   - Creates the metadata file only for manual attachment.
   - For automatic attachment, the metadata file must already exist.
8. Release the resource.
9. Release the local context reference in all cases.

If the failure is simply unsupported volume/device and the attach was automatic, the status is converted to `STATUS_FLT_DO_NOT_ATTACH` to avoid noisy error logging.

## `FmmInstanceQueryTeardown`

Always permits manual detach by returning `STATUS_SUCCESS`.

It is present to show where a real filter could reject detach requests.

## `FmmInstanceTeardownStart`

Logs teardown start/end and does no state mutation.

## `FmmInstanceTeardownComplete`

Completes cleanup for an instance:

- Gets the instance context.
- Acquires `MetadataResource` exclusive.
- Asserts the context is not in transition.
- If metadata is open, calls `FmmCloseMetadata`.
- Releases the resource.
- Releases the context reference.

This ensures the metadata file handle/object are closed before the context cleanup deletes the resource.

## Research Notes

This file defines the sample’s attach policy and lifecycle boundaries. The key relationship is:

- `MetadataManagerInit.c` creates and owns `FMM_INSTANCE_CONTEXT`.
- `DataStore.c` manages metadata-file state inside that context.
- `operations.c` triggers release/reacquire based on filesystem operations.

The sample intentionally attaches only when metadata exists on automatic mount, while manual attach can create the metadata file.
