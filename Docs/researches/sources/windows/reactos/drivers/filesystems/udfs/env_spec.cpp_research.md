# File Research: sources/windows/reactos/drivers/filesystems/udfs/env_spec.cpp

## Purpose

`env_spec.cpp` provides NT-kernel environment-specific physical I/O helpers for UDFS. It builds lower-level read, write, and IOCTL IRPs against the target device, waits for completion, bridges completion status back to UDFS callers, implements optional debug/performance instrumentation, and supplies debug notification wrappers.

## Main Entry Points

- `UDFAsyncCompletionRoutine(PDEVICE_OBJECT, PIRP, PVOID)`: completion routine for asynchronous read/write IRPs built at elevated IRQL. It copies I/O status, unlocks and frees MDLs, frees the IRP, signals the context event, and returns `STATUS_MORE_PROCESSING_REQUIRED`.
- `UDFSyncCompletionRoutine(PDEVICE_OBJECT, PIRP, PVOID)`: completion routine that copies I/O status into the context and returns success. It is currently not active in the IOCTL path.
- `UDFPhReadSynchronous(PDEVICE_OBJECT, PVOID, SIZE_T, LONGLONG, PSIZE_T, ULONG)`: reads bytes from the physical target device, using synchronous or asynchronous FSD request construction depending on current IRQL.
- `UDFPhWriteSynchronous(PDEVICE_OBJECT, PVOID, SIZE_T, LONGLONG, PSIZE_T, ULONG)`: writes bytes to the physical target device, using synchronous or asynchronous FSD request construction depending on current IRQL.
- `UDFTSendIOCTL(ULONG, PVCB, PVOID, ULONG, PVOID, ULONG, BOOLEAN, PIO_STATUS_BLOCK)`: serializes a target-device IOCTL through `Vcb->IoResource` and delegates to `UDFPhSendIOCTL`.
- `UDFPhSendIOCTL(ULONG, PDEVICE_OBJECT, PVOID, ULONG, PVOID, ULONG, BOOLEAN, PIO_STATUS_BLOCK)`: builds and sends a device IOCTL request to a physical device and waits for completion if pending.
- `UDFNotifyFullReportChange(...)` and `UDFNotifyVolumeEvent(...)`: debug-build notification wrappers; non-debug builds use inline/macro definitions from `env_spec.h`.

## Physical Read Behavior

`UDFPhReadSynchronous` sets `*ReadBytes` to zero, optionally uses the caller buffer directly when `PH_TMP_BUFFER` is set, otherwise allocates a nonpaged temporary buffer. It allocates a `UDF_PH_CALL_CONTEXT`, initializes a notification event, builds either an asynchronous or synchronous `IRP_MJ_READ` request, sets `SL_OVERRIDE_VERIFY_VOLUME`, calls the lower driver, and waits when the status is `STATUS_PENDING`.

On success, it copies the completed byte count from the context status block, copies temporary-buffer contents back to the caller buffer when used, optionally mirrors reads into `UDFVRead` for browse/debug builds, records performance counters when enabled, frees context and temporary buffer, and returns normalized status. `STATUS_DATA_OVERRUN` is treated as success after completion.

## Physical Write Behavior

`UDFPhWriteSynchronous` is analogous to read but sends `IRP_MJ_WRITE`. In debug builds, `UDF_SIMULATE_WRITES` can short-circuit writes by pretending all bytes were written. The current active implementation writes directly from the caller buffer rather than copying to a temporary buffer. It sets `SL_OVERRIDE_VERIFY_VOLUME`, waits for pending completion, updates `*WrittenBytes`, optionally mirrors writes into `UDFVWrite`, records performance counters, and logs write failures.

`UDFPhWriteVerifySynchronous` exists only inside `#if 0`; the public header maps write-verify to ordinary write.

## IOCTL Behavior

`UDFTSendIOCTL` acquires `Vcb->IoResource` exclusively with a check helper, then calls `UDFPhSendIOCTL` against `Vcb->TargetDeviceObject`, releasing the resource in `finally`.

`UDFPhSendIOCTL` allocates a context, initializes an event, builds an IOCTL IRP with `IoBuildDeviceIoControlRequest`, optionally sets `SL_OVERRIDE_VERIFY_VOLUME`, calls the driver, waits for pending completion, normalizes `STATUS_DATA_OVERRUN` to success, copies the completion IOSB to the optional caller-supplied IOSB, frees context, and returns the final status. If waiting above passive level, it uses a short timeout that doubles until completion.

## Notification Helpers

In debug builds, `UDFNotifyFullReportChange` wraps `FsRtlNotifyFullReportChange`, computing the parent prefix length differently for root versus non-root objects. `UDFNotifyVolumeEvent` is stubbed to return because the ReactOS FIXME indicates `FsRtlNotifyVolumeEvent` is effectively unavailable or intentionally disabled.

## Instrumentation

`MEASURE_IO_PERFORMANCE` enables global counters for read time, write time, written data, and relative write time, with `PerfPrint` timing output. Debug builds expose `UDF_SIMULATE_WRITES`.

## Integration Points

These helpers are used broadly by physical/media code under `Include/phys_lib.cpp`, format support, verify support, eject handling, close/reset paths, and filesystem control paths. They are declared by `env_spec.h`, while a Win32 user-mode analogue exists under `Include/env_spec_w32.cpp`.

## Notable Risks and Edge Cases

- The functions wait for I/O even when they may be called above passive level; read/write use asynchronous FSD requests at elevated IRQL, while IOCTL waits assert below dispatch level and uses timeout polling above passive.
- `UDFAsyncCompletionRoutine` frees the IRP and MDLs itself and returns `STATUS_MORE_PROCESSING_REQUIRED`; callers must not touch the IRP afterward.
- Read uses a temporary buffer unless `PH_TMP_BUFFER` is set, while write currently writes directly from caller memory; buffer lifetime and nonpaged residency matter.
- `IoBuildSynchronousFsdRequest` usually signals the event itself; the sync completion routine is mostly unused/commented.
- `UDFPhSendIOCTL` does not install a completion routine in the active path, relying on the built IOCTL request event and IO status block.
- Optional `_BROWSE_UDF_` behavior overloads the byte-count pointer as a VCB carrier when `PH_VCB_IN_RETLEN` is set.

## Testing Signals

Useful tests would mock lower-device completion for immediate success, pending success, `STATUS_DATA_OVERRUN`, failure, missing IRP allocation, temporary read-buffer copyback, simulated writes, override-verify flag propagation, serialized `UDFTSendIOCTL`, and elevated-IRQL asynchronous read/write completion cleanup.
