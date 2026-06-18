# File Research: sources/windows/windows-driver-samples/filesys/fastfat/workque.c

## Role

`workque.c` implements FastFAT request posting to filesystem worker threads. It prepares IRPs that cannot complete synchronously, handles oplock completion reposting, locks user buffers before returning pending, and throttles per-volume worker concurrency with an overflow queue.

## Key Routines

- `FatOplockComplete`: callback from the oplock package. Successful oplock completion queues the request to the FastFAT work queue; failure completes the IRP immediately.
- `FatPrePostIrp`: prepares an IRP before the FSD returns `STATUS_PENDING`. It clears stack-based `FatIoContext` references, probes/locks user buffers for read, write, directory query, EA query/set, and selected FSCTL output buffers, then calls `IoMarkIrpPending`.
- `FatFsdPostRequest`: standard FSD helper that calls `FatPrePostIrp`, queues the request, and returns `STATUS_PENDING`.
- `FatAddToWorkque`: queues an IRP context to `CriticalWorkQueue`, or places it on the volume overflow queue if more than `FSP_PER_DEVICE_THRESHOLD` requests are already posted for that volume.

## Important Mechanics

The file enforces a per-device worker threshold of two posted requests. Additional requests with a file object are stored on the volume device object’s `OverflowQueue` under `OverflowQueueSpinLock`, preventing unbounded worker-thread fan-out for one target device.

User buffers are locked before posting because the original caller’s context may be gone when the worker thread later resumes processing. MDL read/write requests are excluded because there is no ordinary user buffer to lock.

## Dependencies And Coupling

This file is coupled to FastFAT’s FSD/FSP split, oplock callbacks, IRP context lifetime, volume device overflow queues, buffer-locking helpers, and Windows executive work items. It is the async handoff point used when requests cannot wait, need oplock continuation, or must resume in worker-thread context.
