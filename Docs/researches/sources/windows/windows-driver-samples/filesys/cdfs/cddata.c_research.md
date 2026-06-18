# File Research: sources/windows/windows-driver-samples/filesys/cdfs/cddata.c

## Purpose

`cddata.c` defines CDFS global data and constants, the common FSD dispatch entry point, exception handling/completion paths, top-level thread context handling, fast-I/O feasibility checks, and a serial checksum helper.

## Global Data and Constants

- Defines global `CdData` and `CdFastIoDispatch`.
- Defines reserved names for `"."` and `".."`.
- Defines volume descriptor IDs for HSG, ISO, and XA.
- Defines audio-disc label and pseudo audio track filename metadata.
- Defines Joliet escape sequences.
- Defines hard-coded RIFF headers:
  - `CdAudioPlayHeader`
  - `CdXAAudioPhileHeader`
  - `CdXAFileHeader`
- Optionally defines `CdTelemetryData` under `CDFS_TELEMETRY_DATA`.

## Dispatch Flow

`CdFsdDispatch` is the common driver entry for major IRP functions registered by `DriverEntry`.

It:

- Enters filesystem context with `FsRtlEnterFileSystem`.
- Determines waitability from mount context or synchronous IRP state.
- Allocates an `IRP_CONTEXT`.
- Sets CDFS top-level thread context.
- Switches on `MajorFunction` and calls:
  - `CdCommonCreate`
  - `CdCommonClose`
  - `CdCommonRead`
  - `CdCommonWrite`
  - `CdCommonQueryInfo`
  - `CdCommonSetInfo`
  - `CdCommonQueryVolInfo`
  - `CdCommonDirControl`
  - `CdCommonFsControl`
  - `CdCommonDevControl`
  - `CdCommonLockControl`
  - `CdCommonCleanup`
  - `CdCommonPnp`
  - `CdCommonShutdown`
- Routes `IRP_MJ_READ` + `IRP_MN_COMPLETE` to `CdCompleteMdl`.
- Uses `CdExceptionFilter` and `CdProcessException`.
- Retries when status is `STATUS_CANT_WAIT`.

## Exception Handling

- `CdRaiseStatusEx`
  - In sanity builds, traces/breaks on selected raised statuses.
  - Stores normalized or raw status in `IrpContext->ExceptionStatus`.
  - Records bug-check file/line into `RaisedAtLineFile`.
  - Raises via `ExRaiseStatus`.

- `CdExceptionFilter`
  - Converts `STATUS_IN_PAGE_ERROR` to underlying I/O status when available.
  - Preserves explicit CDFS-raised status.
  - Bugchecks unexpected NTSTATUS exceptions via `CdBugCheck`.
  - Returns `EXCEPTION_EXECUTE_HANDLER` for expected statuses.

- `CdProcessException`
  - Handles posting/retry decisions for `STATUS_CANT_WAIT` and verify-required cases.
  - Performs media verification through `CdPerformVerify` when possible.
  - Raises hard errors for user-induced conditions unless disabled.
  - Completes regular failures through `CdCompleteRequest`.

- `CdCompleteRequest`
  - Cleans up the IRP context.
  - Clears `IoStatus.Information` for input operations that fail.
  - Sets final IRP status and completes with `IO_CD_ROM_INCREMENT`.

## Other Routines

- `CdSetThreadContext`
  - Manages CDFS top-level IRP context stored in `IoGetTopLevelIrp`.
  - Detects whether an existing top-level context is a valid stack-resident CDFS context.
  - Records prior top-level value for later restore.

- `CdFastIoCheckIfPossible`
  - Allows fast I/O only for user file reads.
  - Rejects non-read checks with `STATUS_INVALID_PARAMETER`.
  - Uses file locks to decide if fast read can proceed.

- `CdSerial32`
  - Generates a 32-bit serial by accumulating bytes into four checksum lanes.

## Integration

This file is the bridge between I/O manager dispatch, CDFS common operation modules, exception-driven error propagation, verify/remount handling, and fast-I/O dispatch initialized in `cdinit.c`.

## Risk Notes

- Exception status stored in `IrpContext` is authoritative once CDFS raises explicitly.
- Verify-required handling carefully avoids trusting potentially invalid thread verify device pointers and falls back to `Vcb->Vpb->RealDevice`.
- Thread-context validation uses stack bounds, alignment, and a CDFS signature; misuse would corrupt top-level IRP handling.
