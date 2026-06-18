# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/iocomp.c

This file implements ReactOS I/O completion objects, modeled as Object Manager objects backed by kernel queues. It also provides completion-packet allocation/freeing and an unload-safe completion routine wrapper.

Global state:
- `IoCompletionType` is the Object Manager type for I/O completion objects.
- `IoCompletionPacketLookaside` is declared for completion packet allocation support.
- `IopCompletionMapping` maps generic rights to `IO_COMPLETION_QUERY_STATE`, `IO_COMPLETION_MODIFY_STATE`, `SYNCHRONIZE`, and `IO_COMPLETION_ALL_ACCESS`.
- `IoCompletionInfoClass` describes `IoCompletionBasicInformation` query validation.

Internal helpers:
- `IopUnloadSafeCompletion` wraps a caller completion routine for `IoSetCompletionRoutineEx`. It references the device object before invoking the real completion routine, dereferences afterward, frees the wrapper context, and returns the real routine status.
- `IopFreeMiniPacket` returns mini completion packets to the per-processor P lookaside list, then the L lookaside list, and finally frees to pool if both lists are at depth.
- `IopDeleteIoCompletion` runs down the queue at object deletion. It frees queued IRP-backed packets with `IoFreeIrp` and non-IRP mini packets through `IopFreeMiniPacket`.

Completion insertion:
- `IoSetIoCompletion` allocates an `IOP_MINI_COMPLETION_PACKET` from the current processor lookaside lists or nonpaged pool, fills key context, APC context, status, and information, then inserts it into the target `KQUEUE`.
- The `Quota` parameter is accepted but not used in the implementation.

Unload-safe completion routines:
- `IoSetCompletionRoutineEx` allocates an `IO_UNLOAD_SAFE_COMPLETION_CONTEXT`, stores the target device, user context, and completion routine, then installs `IopUnloadSafeCompletion` as the IRP completion routine.

Nt entry points:
- `NtCreateIoCompletion` probes the output handle for user callers, creates an `IoCompletionType` object sized as a `KQUEUE`, initializes the queue with the requested concurrency count, inserts the object, and returns the handle.
- `NtOpenIoCompletion` opens an existing completion object by name and returns a handle.
- `NtQueryIoCompletion` validates query buffers, references the completion object with `IO_COMPLETION_QUERY_STATE`, returns queue depth as `IO_COMPLETION_BASIC_INFORMATION.Depth`, and optionally writes the result length.
- `NtRemoveIoCompletion` references the queue with `IO_COMPLETION_MODIFY_STATE`, removes the next queued entry with optional timeout, distinguishes timeout/user APC status from real list entries, handles both IRP-backed completion packets and mini packets, writes key/APC/status results, and dereferences the queue.
- `NtSetIoCompletion` references the queue with modify access and delegates packet insertion to `IoSetIoCompletion`.

Research notes:
- The queue stores two packet shapes: IRP-backed entries where `IRP.Tail.Overlay.ListEntry` is embedded, and standalone `IOP_MINI_COMPLETION_PACKET` entries allocated from lookaside/pool.
- `NtRemoveIoCompletion` frees IRPs after extracting completion data, so ownership transfers to the completion port queue before removal.
- User buffer probing and result writes are consistently wrapped in SEH.
- The implementation depends on per-processor lookaside accounting fields (`TotalAllocates`, `AllocateMisses`, `TotalFrees`, `FreeMisses`) being updated manually.
