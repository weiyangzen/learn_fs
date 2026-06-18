# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/cdo/CdoProc.h

## Purpose

Declares the CDO sample’s internal functions and inline resource helpers.

## API Surface

- Declares CDO lifecycle functions: `CdoCreateControlDeviceObject()` and `CdoDeleteControlDeviceObject()`.
- Declares `CdoMajorFunction()` and private IRP handlers for open, cleanup, close, and FS-control.
- Declares all Fast I/O callback functions installed in `CdoFastIoDispatch`.
- Provides inline wrappers:
  - `CdoAcquireResourceExclusive()`
  - `CdoAcquireResourceShared()`
  - `CdoReleaseResource()`

## Resource Semantics

- Acquisition wrappers assert `KeGetCurrentIrql() <= APC_LEVEL`.
- They enter a critical region before acquiring the `ERESOURCE`, preventing normal kernel APC delivery while the resource is held.
- Release asserts the resource is held, releases it, and leaves the critical region.

## Dependencies

- Uses kernel driver annotations, `PERESOURCE`, `PDEVICE_OBJECT`, `PIRP`, Fast I/O types, and file information structures from the WDK headers included through `pch.h`.
- Function declarations match implementations in `CdoOperations.c`.

## Risks And Invariants

- Inline resource helpers must be paired exactly. Holding the resource also means the current thread is in a critical region.
- The annotations describe expected lock ownership for static analysis and should remain aligned with the implementation.
- The header is internal to the sample and assumes `CdoStruct.h`/WDK types are already available through `pch.h`.
