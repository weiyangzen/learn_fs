# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/scanner/filter/scanner.h

Kernel-only scanner minifilter header.

Key contents:
- Defines `SCANNER_DATA`, the global driver state: driver object, filter handle, server port, trusted user process, and client port.
- Declares external global `ScannerData`.
- Defines `SCANNER_STREAM_HANDLE_CONTEXT` with `BOOLEAN RescanRequired`.
- Defines unused/placeholder `SCANNER_CREATE_PARAMS` with a zero-length `WCHAR String[0]`.
- Declares `DriverEntry`, unload, teardown query, create/post-create, cleanup, write, Win8+ file-system-control, and instance setup routines.

Important behavior:
- The stream-handle context is the driver’s main per-open state and controls cleanup rescanning.
- Function prototypes match the FltMgr callback signatures used in `scanner.c`.

Dependencies and risks:
- The module comment says `scrubber.h`, but the guard and file role are scanner-specific.
- `SCANNER_DATA.DriverObject` is defined here, though this source file does not use it meaningfully.
