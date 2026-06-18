# File Research: sources/windows/reactos/drivers/filesystems/cdfs/cddata.c

## Purpose

`cddata.c` owns CDFS global runtime data and the top-level FSD dispatch/exception path. It defines global constants used across the driver, then implements request entry, exception normalization/retry/posting, request completion, thread top-level context tracking, fast-I/O admission, and a simple volume serial checksum helper.

## Key Contents

- Global objects:
  - `CD_DATA CdData`
  - `FAST_IO_DISPATCH CdFastIoDispatch`
  - directory pseudo-names `.` and `..`
  - ISO/HSG/XA volume identifier strings
  - audio CD label and synthetic track filename metadata
  - Joliet escape strings
  - hardcoded RIFF/CDDA/CDXA header templates for audio and XA exposure
  - optional `CDFS_TELEMETRY_DATA_CONTEXT CdTelemetryData`

- `CdFsdDispatch`
  - Main dispatch routine for `IRP_MJ_CREATE`, `CLOSE`, `READ`, `WRITE`, query/set information, volume info, directory control, FS/device/lock control, cleanup, PnP, and shutdown.
  - Enters the filesystem with `FsRtlEnterFileSystem`.
  - Creates an `IRP_CONTEXT` on first pass using `CdCreateIrpContext`.
  - Determines waitability from mount/file-object state via `CanFsdWait`.
  - Sets top-level thread context with `CdSetThreadContext`.
  - Retries while status is `STATUS_CANT_WAIT`.
  - Uses SEH and delegates exception filtering/processing to `CdExceptionFilter` and `CdProcessException`.

- `CdRaiseStatusEx`
  - Debug/sanity-only implementation that records raised status, optional normalization, source file/line encoding, and optional breakpoint behavior.
  - Release inline equivalent is declared in `cdprocs.h`.

- `CdExceptionFilter`
  - Converts `STATUS_IN_PAGE_ERROR` to the underlying I/O error when available.
  - Stores the exception in `IrpContext->ExceptionStatus` if CDFS did not already raise one.
  - Bugchecks for unexpected NTSTATUS values via `FsRtlIsNtstatusExpected`.

- `CdProcessException`
  - Handles posting, retry, verify-required, user-induced errors, hard-error popup generation, and final completion.
  - Posts `STATUS_CANT_WAIT` requests when forced.
  - Posts `STATUS_VERIFY_REQUIRED` when top-level and APCs are disabled.
  - For verify-required, finds or substitutes the real device object and calls `CdPerformVerify`.
  - For other user-induced errors, either completes immediately if popups are disabled or calls `IoRaiseHardError`.
  - Normal errors complete through `CdCompleteRequest`.

- `CdCompleteRequest`
  - Cleans up the `IRP_CONTEXT`.
  - Zeros `IoStatus.Information` for failed input operations.
  - Sets final IRP status and completes via `IoCompleteRequest`.

- `CdSetThreadContext`
  - Manages CDFS top-level request context using `IoGetTopLevelIrp` / `IoSetTopLevelIrp`.
  - Validates existing thread context by stack location, alignment, and signature.
  - ReactOS path uses `IoGetStackLimits` instead of `IoWithinStackLimits`.
  - Marks top-level CDFS ownership with `IRP_CONTEXT_FLAG_TOP_LEVEL_CDFS`.

- `CdFastIoCheckIfPossible`
  - Allows fast I/O only for user file reads.
  - Rejects writes/non-file opens with `STATUS_INVALID_PARAMETER`.
  - Checks byte-range locks with `FsRtlFastCheckLockForRead`.

- `CdSerial32`
  - Builds a 32-bit serial by summing bytes into four checksum lanes and returning them as a `ULONG`.

## Dependencies and Interactions

- Included through `cdprocs.h`, so it depends on all core CDFS structures and declarations.
- Dispatch targets are implemented in operation-specific files such as `create.c`, `read.c`, `cleanup.c`, `close.c`, `fsctrl.c`, etc.
- Exception flow is tightly coupled to `IRP_CONTEXT` fields from `cdstruc.h`.
- Fast I/O checks depend on `CdFastDecodeFileObject`, `CdIsFastIoPossible`, oplock/file-lock state, and FSRTL lock helpers.
- Verify and dismount behavior depends on VCB state and device verification helpers.

## Behavioral Notes

- `STATUS_CANT_WAIT` is an internal retry/posting signal, not a final caller status.
- Top-level context preservation is critical because recursive filesystem entry can occur during cache manager, memory manager, verify, or hard-error paths.
- The file is mostly infrastructure; actual filesystem semantics are delegated through the major-function switch.
- Audio/XA headers expose CD audio and CD-XA data as synthetic RIFF-style files without dynamically allocating these templates per request.
