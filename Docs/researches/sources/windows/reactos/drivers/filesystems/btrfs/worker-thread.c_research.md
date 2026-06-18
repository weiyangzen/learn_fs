# File Research: sources/windows/reactos/drivers/filesystems/btrfs/worker-thread.c

## Role

This file provides a small delayed-work-queue wrapper for Btrfs read and write IRPs that cannot complete immediately. It packages an IRP and optional VCB pointer into a `WORK_QUEUE_ITEM`, queues it to `DelayedWorkQueue`, and completes the IRP from the worker routine after running the normal read or write path synchronously.

## Major Responsibilities

- Execute deferred read work through `do_read_job()`.
- Execute deferred write work through `do_write_job()`.
- Allocate and initialize `job_info` records.
- Ensure user buffers have an MDL and locked pages before a job leaves the caller context.
- Queue the worker item and free the `job_info` after execution.

## Read Job

`do_read_job()`:

- Determines whether this IRP was set as top-level via `is_top_level()`.
- Gets the `FILE_OBJECT` and FCB.
- Initializes `IoStatus.Information` to zero.
- Acquires the FCB main resource shared if the current thread does not already hold it shared.
- Calls `do_read(Irp, true, &bytes_read)` inside an SEH guard.
- Releases the FCB resource if it acquired it.
- Stores the resulting status, logs failures, completes the IRP, clears top-level IRP state if needed, and returns the status.

The `bytes_read` local is passed to `do_read()` but this wrapper relies on `Irp->IoStatus.Information` for the completed byte count.

## Write Job

`do_write_job()`:

- Captures top-level IRP state.
- Calls `write_file(Vcb, Irp, true, true)` inside an SEH guard, forcing wait/deferred-write behavior appropriate for queued execution.
- Stores the status, logs failures, completes the IRP, clears top-level IRP state if needed, and returns the status.

## Worker Dispatch

`do_job()` gets the current IRP stack location and dispatches by `MajorFunction`:

- `IRP_MJ_READ` -> `do_read_job()`
- `IRP_MJ_WRITE` -> `do_write_job()`

It frees the `job_info` after dispatch. The code assumes `ji->Irp` is non-null before dereferencing `IrpSp`; the ternary assignment allows null but the subsequent `IrpSp->MajorFunction` does not.

## Queue Setup And MDL Preparation

`add_thread_job()` allocates a nonpaged `job_info`, stores the VCB and IRP, and ensures `Irp->MdlAddress` exists:

- For read IRPs, it probes with `IoWriteAccess` because the device will write into the user buffer.
- For write IRPs, it probes with `IoReadAccess` because the device will read from the user buffer.
- It derives length from the read/write parameters.
- It rejects unexpected major functions.
- It allocates an MDL over `Irp->UserBuffer`, attaches it to the IRP, and probes/locks pages under SEH.
- On probe failure, it frees the MDL, clears `Irp->MdlAddress`, frees the job record, and returns false.

If MDL setup succeeds or an MDL was already present, the function initializes the work item and queues it.

## Dependencies And Integration Points

This file depends on `btrfs_drv.h`, `do_read()`, `write_file()`, `is_top_level()`, FCB resource state, Windows MDL probing/locking APIs, and the delayed work queue. It is called by dispatch paths such as `drv_write()` when `write_file()` returns `STATUS_PENDING`.

## Risk Notes

- `do_job()` does not guard against `ji->Irp == NULL` after assigning `IrpSp`.
- MDLs allocated here are not freed in this file; freeing is expected later in normal IRP completion/cleanup paths.
- Queued read jobs acquire the FCB resource shared only if not already held shared; they do not check exclusive ownership separately.
