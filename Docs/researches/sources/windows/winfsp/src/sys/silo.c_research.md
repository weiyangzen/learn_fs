# File Research: sources/windows/winfsp/src/sys/silo.c

## Purpose

`silo.c` adds Windows Server silo/container awareness to WinFsp. It dynamically loads silo monitor APIs on supported Windows versions, creates per-silo global state, and runs WinFsp initialization/finalization callbacks inside each server silo context.

## Main Contents

- Local typedefs for silo-related Windows kernel APIs.
- Dynamically loaded function pointers for `PsRegisterSiloMonitor`, `PsGetSiloContext`, `PsAttachSiloToCurrentThread`, and related APIs.
- Global monitor state:
  - `FspSiloMonitor`
  - init/fini callbacks
  - `FspSiloInitDone`
  - `FspSiloListMutex`
  - `FspSiloList`
  - host fallback globals
- Public API:
  - `FspSiloIsHost`
  - `FspSiloGetGlobals`
  - `FspSiloDereferenceGlobals`
  - `FspSiloGetContainerId`
  - `FspSiloInitialize`
  - `FspSiloPostInitialize`
  - `FspSiloFinalize`
  - `FspSiloEnumerate`

## Initialization

`FspSiloInitialize`:

- Initializes the silo list mutex and list.
- Checks for Windows 10 RS5 or newer.
- Dynamically resolves all required silo APIs with `MmGetSystemRoutineAddress`.
- Registers a silo monitor with create and terminate callbacks.
- Stores WinFsp init/fini callbacks and marks silo support initialized.
- If the OS or APIs are unavailable, it leaves silo support disabled but returns success.

`FspSiloPostInitialize` starts the registered monitor after primary initialization.

## Silo Creation

`FspSiloMonitorCreateCallback`:

- Gets the monitor context slot.
- Creates a `FSP_SILO_GLOBALS` silo context.
- Inserts it into the silo.
- Enters filesystem context and locks the silo list.
- Attaches the current thread to the new silo and invokes the WinFsp init callback.
- On success, inserts the globals into the global silo list.
- On failure, removes inserted context and dereferences globals.
- Always returns `STATUS_SUCCESS` to avoid blocking container creation or triggering known Windows crashes.

## Silo Termination

`FspSiloMonitorTerminateCallback`:

- Retrieves silo globals.
- Removes them from the global list.
- Attaches to the terminating silo and invokes the WinFsp fini callback.
- Removes the silo context, dropping the monitor's reference.

## Global Lookup

- `FspSiloIsHost` reports host mode before initialization or when no current server silo exists.
- `FspSiloGetGlobals` returns host globals outside a silo, otherwise returns the current silo context and leaves it referenced.
- `FspSiloDereferenceGlobals` dereferences only real silo contexts, not host globals.
- `FspSiloGetContainerId` returns the current silo container GUID or a zero GUID for host/no-silo.

## Enumeration

`FspSiloEnumerate`:

- Locks the list.
- Attaches to `PsInitialSystemProcess`.
- Iterates silo globals.
- Attaches the thread to each silo and calls the supplied enumeration callback.

## Notable Details

- The code monitors existing silos as well as future silos.
- Host globals are always available even when silo support is not active.
- Debug finalization asserts that the silo list is empty after unregistering the monitor.
- Silo callbacks deliberately use `FsRtlEnterFileSystem` and `ExAcquireFastMutexUnsafe` around shared list state.
