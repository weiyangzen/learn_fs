# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/cancelSafe/cancelSafe.c

## Purpose

Implements a kernel-mode minifilter sample demonstrating Filter Manager cancel-safe callback data queues (`FltCbdq*`). It delays matching read IRPs for a configurable period, supports cancellation and instance teardown, and completes queued reads safely from a worker item.

## Public And Internal APIs

- Driver lifecycle: `DriverEntry()`, `Unload()`, `FreeGlobals()`.
- Registry configuration: `GetIoOpenDriverRegistryKey()`, `OpenServiceParametersKey()`, `SetConfiguration()`.
- Instance lifecycle: `InstanceSetup()`, `InstanceQueryTeardown()`, `InstanceTeardownStart()`, `InstanceTeardownComplete()`.
- Context cleanup: `ContextCleanup()`.
- Callback data queue hooks: `CsqAcquire()`, `CsqRelease()`, `CsqInsertIo()`, `CsqRemoveIo()`, `CsqPeekNextIo()`, `CsqCompleteCanceledIo()`.
- Read path: `PreRead()`, `PreReadWorkItemRoutine()`, `PreReadPendIo()`, `PreReadProcessIo()`, `PreReadEmptyQueueAndComplete()`.

## Registration And Configuration

- Registers only `IRP_MJ_READ` with `FLTFL_OPERATION_REGISTRATION_SKIP_PAGING_IO`.
- Registers an instance context containing a `FLT_CALLBACK_DATA_QUEUE`, list head, fast mutex, worker flag, and teardown event.
- Initializes a nonpaged lookaside list for per-I/O `QUEUE_CONTEXT` allocations.
- Reads optional service parameters:
  - `DebugLevel` controls `DbgPrint` categories.
  - `OperatingDelay` sets the relative wait delay before completing a pended read.
  - `OperatingPath` selects the parent-directory prefix to delay, defaulting to `\`.
- Uses `IoOpenDriverRegistryKey` when available, with a `ZwOpenKey` fallback for older systems.

## Control Flow

- `DriverEntry()` opts into `NonPagedPoolNx`, initializes defaults and lookaside storage, applies registry configuration, registers the minifilter, and starts filtering.
- `InstanceSetup()` allocates and initializes an `INSTANCE_CONTEXT`, initializes the CBDQ with this file’s queue callbacks, initializes `QueueHead`, `Lock`, `WorkerThreadFlag`, and `TeardownEvent`, then attaches the context to the instance.
- `PreRead()` skips paging I/O, synchronous paging I/O, and non-null `TopLevelIrp`; it obtains normalized file name information, parses it, checks whether `Globals.MappingPath` prefixes the parent directory, disallows fast I/O for matched files, allocates a queue context, gets the instance context, stores queue context pointers in `Data->QueueContext`, and inserts the operation with `FltCbdqInsertIo()`.
- `CsqInsertIo()` inserts callback data at the tail of the internal list. If the queue was empty and no worker is active, it allocates and queues a generic work item. If work-item creation fails, it decrements the worker flag and removes the just-inserted operation.
- `PreReadWorkItemRoutine()` gets the instance context, repeatedly waits `Globals.TimeDelay` or until teardown, removes the next queued I/O, calls `PreReadProcessIo()`, locks user buffers when required, completes the pended pre-operation, frees the queue context, and exits only when the queue is empty and the worker flag race resolves to zero.
- `InstanceTeardownStart()` disables further CBDQ insertion, drains queued I/O through `PreReadEmptyQueueAndComplete()`, and signals the teardown event to wake a waiting worker.
- `CsqCompleteCanceledIo()` completes canceled pended operations with `STATUS_CANCELLED` and frees the per-I/O queue context.

## State And Data Structures

- `CSQ_GLOBAL_DATA` contains debug level, filter handle, queue-context lookaside list, configured mapping path buffer/string, and delay interval.
- `INSTANCE_CONTEXT` contains the Filter Manager instance pointer, the CBDQ object, private list head, fast mutex, worker-thread presence flag, and teardown event.
- `QUEUE_CONTEXT` wraps `FLT_CALLBACK_DATA_QUEUE_IO_CONTEXT`, which Filter Manager uses for cancel-safe tracking.
- The private list uses `FLT_CALLBACK_DATA.QueueLinks`.

## Dependencies

- Filter Manager kernel APIs: `FltRegisterFilter`, `FltStartFiltering`, `FltAllocateContext`, `FltSetInstanceContext`, `FltGetInstanceContext`, `FltCbdqInitialize`, `FltCbdqInsertIo`, `FltCbdqRemoveNextIo`, `FltCbdqDisable`, `FltCompletePendedPreOperation`, `FltAllocateGenericWorkItem`, `FltQueueGenericWorkItem`, `FltFreeGenericWorkItem`, `FltGetFileNameInformation`, `FltParseFileNameInformation`, `FltLockUserBuffer`.
- Kernel synchronization/allocation: fast mutexes, events, interlocked operations, nonpaged lookaside lists, registry Zw APIs.
- Name filtering depends on normalized file names and `RtlPrefixUnicodeString()` against the parent directory.

## Risks And Invariants

- Queue lock callbacks use a fast mutex, so they run at APC-level constraints and store a dummy IRQL value.
- The worker flag is the central race-control invariant. `CsqInsertIo()` increments it when adding work to an empty queue; the worker reduces it to one before removing I/O and decrements on empty to decide whether to exit or continue after racing inserts.
- Fast I/O cannot be queued; matched Fast I/O reads are rejected with `FLT_PREOP_DISALLOW_FASTIO` to force the request down the IRP path for demonstration.
- User buffers must be locked before completing a pended operation in a different process context unless the data is already system-buffered or has an MDL.
- Teardown must disable the CBDQ before draining; otherwise new inserts could race with queue drain.
- `PreReadProcessIo()` is intentionally a stub returning success; this sample demonstrates queueing/cancellation rather than data inspection.
