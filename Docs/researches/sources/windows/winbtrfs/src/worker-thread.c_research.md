# File Research: sources/windows/winbtrfs/src/worker-thread.c

## Purpose

`worker-thread.c` provides deferred worker-queue execution for WinBtrfs read and write IRPs. It lets dispatch paths queue work that cannot complete immediately, then performs the actual read/write on a system worker thread and completes the IRP.

## Main Data Structure

`job_info` stores the target `device_extension`, queued `PIRP`, and embedded `WORK_QUEUE_ITEM`.

## Deferred Read Path

`do_read_job` runs a queued read. It detects top-level IRP state, obtains the file object's FCB, clears `IoStatus.Information`, acquires the FCB resource shared if the current thread does not already hold it, calls `do_read(Irp, true, &bytes_read)` inside structured exception handling, releases the resource if acquired, logs failures, sets `Irp->IoStatus.Status`, completes the IRP, clears top-level IRP state if needed, and returns the status.

## Deferred Write Path

`do_write_job` runs a queued write. It detects top-level IRP state, calls `write_file(Vcb, Irp, true, true)` inside structured exception handling, logs failures, sets IRP status, completes the IRP, clears top-level IRP state if needed, and returns the status.

## Worker Dispatch and Queuing

`do_job` is the `WORKER_THREAD_ROUTINE`. It inspects the queued IRP major function and dispatches to `do_read_job` for `IRP_MJ_READ` or `do_write_job` for `IRP_MJ_WRITE`, then frees `job_info`.

`add_thread_job` allocates `job_info`, stores the VCB and IRP, and ensures the IRP has an MDL. If no MDL is present it allocates one over `Irp->UserBuffer` and probes/locks pages with `IoWriteAccess` for reads or `IoReadAccess` for writes. It then initializes and queues the work item to `DelayedWorkQueue`.

## Dependencies and Cross-File Interactions

This file calls `do_read` from the read path and `write_file` from the write path, uses FCB resources from `btrfs_drv.h`, and relies on Windows work queue, MDL, probe/lock, exception, and IRP completion APIs.

It is used by dispatch code that marks an IRP pending and needs the operation continued outside the caller's original context.

## Error Handling and Safety Notes

Allocation failures and page-probe exceptions cause `add_thread_job` to clean up and return false so the caller can fail or complete the IRP. The read job acquires the FCB resource only if needed, avoiding recursive acquisition when already held.

`do_job` computes `IrpSp` as nullable but then dereferences it without a null check. In current use `job_info->Irp` is always set by `add_thread_job`, so this is an internal invariant rather than a general-purpose worker routine.
