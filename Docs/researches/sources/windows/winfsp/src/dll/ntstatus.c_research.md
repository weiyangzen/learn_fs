# File Research: sources/windows/winfsp/src/dll/ntstatus.c

This file maps between Win32 errors and NTSTATUS values.

Key responsibilities:
- Lazily resolves `RtlNtStatusToDosError` from `ntdll.dll`.
- `FspNtStatusFromWin32` uses generated mappings from `ntstatus.i`; unknown 16-bit Win32 errors become `FACILITY_NTWIN32` HRESULT-style NTSTATUS values, while larger unknown errors become `STATUS_ACCESS_DENIED`.
- `FspWin32FromNtStatus` delegates to `RtlNtStatusToDosError`, returning `ERROR_MR_MID_NOT_FOUND` if unavailable.

Filesystem relevance:
- Error translation is used throughout the DLL when bridging Windows API failures, launcher/provider errors, and NTSTATUS-returning WinFsp APIs.
