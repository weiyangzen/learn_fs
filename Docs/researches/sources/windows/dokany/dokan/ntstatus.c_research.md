# File Research: sources/windows/dokany/dokan/ntstatus.c

Maps Win32 error codes to NTSTATUS values.

Key behavior:
- `DokanNtStatusFromWin32(DWORD Error)` uses generated include `ntstatus.i` inside a switch.
- Unknown Win32 errors are logged and mapped to `STATUS_ACCESS_DENIED`.

Role:
- Used where Win32 API failures must be returned through Dokan’s NTSTATUS-oriented protocol, such as write request handling.
