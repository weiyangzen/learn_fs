# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/ctx/CtxInit.c

## Purpose
Main initialization and lifecycle module for the `ctx` minifilter sample. It registers the filter, declares operation/context registration tables, handles instance attach/teardown, initializes debug tracing in checked builds, and centralizes cleanup for all context types used by the sample.

## Key Contents
- Defines global `CTX_GLOBAL_DATA Globals`.
- Registers operation callbacks for:
  - `IRP_MJ_CREATE` -> `CtxPreCreate` / `CtxPostCreate`
  - `IRP_MJ_CLEANUP` -> `CtxPreCleanup`
  - `IRP_MJ_CLOSE` -> `CtxPreClose`
  - `IRP_MJ_SET_INFORMATION` -> `CtxPreSetInfo` / `CtxPostSetInfo`
- Registers context types:
  - `FLT_INSTANCE_CONTEXT`
  - `FLT_FILE_CONTEXT`
  - `FLT_STREAM_CONTEXT`
  - `FLT_STREAMHANDLE_CONTEXT`
- Defines `FilterRegistration` with unload and instance lifecycle callbacks.

## Important Functions
- `DriverEntry`
  - Opts into `NonPagedPoolNx` via `ExInitializeDriverRuntime`.
  - Clears `Globals`.
  - Initializes checked-build debug level from registry.
  - Calls `FltRegisterFilter`, then `FltStartFiltering`.
  - Unregisters on start failure.

- `CtxUnload`
  - Unregisters the filter and clears `Globals.Filter`.

- `CtxContextCleanup`
  - Dispatches cleanup by `FLT_CONTEXT_TYPE`.
  - Frees instance volume names, file names, stream names, stream-handle names.
  - Deletes and frees `ERESOURCE` objects in stream and stream-handle contexts.
  - Does not free the context object itself; Filter Manager owns that.

- `CtxInstanceSetup`
  - Allocates an instance context.
  - Queries volume name length with `FltGetVolumeName`.
  - Allocates and fills `VolumeName`.
  - Saves `Instance` and `Volume`.
  - Sets the instance context with `FLT_SET_CONTEXT_KEEP_IF_EXISTS`.
  - Always releases the local allocation reference after attempting to set.

- `CtxInstanceQueryTeardown`
  - Always permits manual detach.

- `CtxInstanceTeardownStart`
  - Trace-only start teardown hook.

- `CtxInstanceTeardownComplete`
  - Retrieves and logs the instance context, then releases it.

## Checked-Build Debug Support
Under `#if DBG`:
- Dynamically resolves `IoOpenDriverRegistryKey` with `MmGetSystemRoutineAddress`.
- Falls back to opening the service registry path and `Parameters` subkey with `ZwOpenKey`.
- Reads `DebugLevel` from registry using `ZwQueryValueKey`.
- Defaults `Globals.DebugLevel` to `DEBUG_TRACE_ERROR`.

## Dependencies
- Uses shared definitions from `pch.h`, `CtxStruc.h`, and `CtxProc.h`.
- Relies on:
  - `CtxAllocateUnicodeString` / `CtxFreeUnicodeString`
  - `CtxFreeResource`
  - operation callbacks implemented in `operations.c`
  - context helper callbacks implemented in `context.c`

## Research Notes
This file demonstrates the Filter Manager reference-count pattern for contexts clearly: after `FltAllocateContext`, the local reference must be released regardless of whether `FltSet*Context` succeeds. Cleanup functions only release subordinate allocations, never the context allocation itself.
