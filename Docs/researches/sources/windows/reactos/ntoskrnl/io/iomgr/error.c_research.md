# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/error.c

This file implements I/O error-log packet allocation, queuing, delivery to the Event Log LPC port, and hard-error mode stubs.

Key behavior:
- Error log entries are capped by `IOP_MAXIMUM_LOG_SIZE` and tracked through `IopTotalLogSize`, `IopErrorLogListHead`, and `IopLogListLock`.
- `IoAllocateErrorLogEntry` accepts either a device object or driver object, validates packet size, references the associated device/driver objects, allocates a nonpaged `ERROR_LOG_ENTRY`, and returns the embedded `IO_ERROR_LOG_PACKET`.
- `IoWriteErrorLogEntry` timestamps the entry, inserts it into the global list, and starts `IopLogWorker` if no worker is running.
- `IopLogWorker` connects to the Event Log port, removes queued entries, builds `ELF_API_MSG` / `IO_ERROR_LOG_MESSAGE` payloads, adds driver and device names plus caller strings, sends them with `ZwRequestPort`, and frees entries on success.
- If port connection or send fails, the worker schedules a delayed retry through a timer/DPC path and requeues the current entry on send failure.
- `IoFreeErrorLogEntry` releases the referenced objects and subtracts the entry size from the global total.
- `IoRaiseHardError` queues a kernel APC to the requesting thread unless hard errors are disabled; the APC target `IopRaiseHardError` is currently unimplemented and completes the IRP with `STATUS_NOT_IMPLEMENTED`.
- `IoRaiseInformationalHardError` is unimplemented and returns `FALSE`.
- `IoSetThreadHardErrorMode` toggles `PsGetCurrentThread()->HardErrorsAreDisabled` and returns the previous enabled state.

Integration points:
- Sends error log messages to the event-log subsystem port named by `ELF_PORT_NAME`.
- Uses object-manager names for driver and device display strings.
- IRP hard-error handling interacts with thread APC state, `VPB`, real device object, and request completion.

Research notes:
- The log-size admission check in `IoAllocateErrorLogEntry` is noted by the code as concurrency-sensitive; it checks `IopTotalLogSize + LogEntrySize` before the interlocked add.
- The queue uses `InsertHeadList` and `RemoveHeadList`, so delivery order is newest-first rather than FIFO.
- Hard-error behavior is mostly placeholder: the queued APC completes with `STATUS_NOT_IMPLEMENTED`, and informational hard errors always fail.
- Driver/device name packing carefully truncates to the fixed LPC message buffer, but that makes long object names lossy in event-log messages.
