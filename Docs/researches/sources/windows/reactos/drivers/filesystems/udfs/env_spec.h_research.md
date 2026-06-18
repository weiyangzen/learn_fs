# File Research: sources/windows/reactos/drivers/filesystems/udfs/env_spec.h

## Purpose

`env_spec.h` declares NT-kernel environment-specific UDFS helper APIs and macros for physical I/O, lower-device IOCTLs, notifications, statistics, thread/PID lookup, and completion routines.

## Declared I/O APIs

- `UDFPhReadSynchronous(...)`: physical-device read helper.
- `UDFPhWriteSynchronous(...)`: physical-device write helper.
- `UDFPhWriteVerifySynchronous`: defined as an alias to `UDFPhWriteSynchronous`; the real verify implementation is disabled in the `.cpp`.
- `UDFTSendIOCTL(...)`: VCB-target IOCTL helper that serializes through VCB I/O resource.
- `UDFPhSendIOCTL(...)`: physical-device IOCTL helper.

Commented-out declarations for asynchronous/background writes remain present but inactive.

## Notification APIs and Macros

Under `UDF_DBG`, the header declares debug implementations of:

- `UDFNotifyFullReportChange(PVCB, PUDF_FILE_INFO, ULONG, ULONG)`
- `UDFNotifyVolumeEvent(PFILE_OBJECT, ULONG)`

Outside debug builds, `UDFNotifyFullReportChange` is an inline wrapper around `FsRtlNotifyFullReportChange` using the file's FCB object name and a parent-prefix length when present. `UDFNotifyVolumeEvent` is a no-op macro with the underlying FsRtl call commented out.

## Statistics Macros

The header defines per-processor statistics increment helpers:

- `CollectStatistics(VCB, Field)`: increments `Statistics[processor].Common.Field`.
- `CollectStatisticsEx(VCB, Field, a)`: adds to `Statistics[processor].Common.Field`.
- `CollectStatistics2(VCB, Field)`: increments `Statistics[processor].Fat.Field`.
- `CollectStatistics2Ex(VCB, Field, a)`: adds to `Statistics[processor].Fat.Field`.

These macros rely on `KeGetCurrentProcessorNumber()` and field-token concatenation.

## Completion and Environment Helpers

Declared completion routines:

- `UDFAsyncCompletionRoutine`
- `UDFSyncCompletionRoutine`
- `UDFSyncCompletionRoutine2`

Small environment macros:

- `UDFGetDevType(DevObj)`: returns `DeviceType`.
- `OSGetCurrentThread()`: maps to `PsGetCurrentThread()`.
- `GetCurrentPID()`: maps to `HandleToUlong(PsGetCurrentProcessId())`.

## Integration Points

This header is included through `udffs.h` into core UDFS dispatch and media code. `create.cpp`, `read.cpp`, `write.cpp`, `fileinfo.cpp`, `cleanup.cpp`, and security support use notification/statistics helpers. Physical read/write/IOCTL helpers are used by verification, mount, formatting, eject, and low-level physical library code.

## Notable Risks

- The notification inline casts `UNICODE_STRING` pointers to `PSTRING`, matching FsRtl's byte-string convention but requiring correct lengths.
- The statistics macros use token-pasting syntax in a macro body; portability depends on the compiler accepting this historical style.
- `UDFNotifyVolumeEvent` is effectively disabled in non-debug builds.
- `GetCurrentPID()` returns a 32-bit `ULONG` handle value, which matches the surrounding lock-owner code but truncates in environments where process IDs are wider.
