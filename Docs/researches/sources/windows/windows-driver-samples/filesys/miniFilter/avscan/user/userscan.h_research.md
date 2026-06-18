# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/userscan.h

## Purpose

Defines the user scanner’s exported API and shared scanner context types for the `avscan` sample’s user-mode component.

## API Surface

- Includes `<windows.h>`, `<fltUser.h>`, and shared `avlib.h`.
- Provides a fallback `MAKE_HRESULT()` macro if the platform headers did not define it.
- Declares `UserScanInit(PUSER_SCAN_CONTEXT Context)` and `UserScanFinalize(PUSER_SCAN_CONTEXT Context)`.

## Data Structures

- `SCANNER_THREAD_CONTEXT` stores one worker’s thread handle, thread ID, current scan ID, abort flag, and critical section used to synchronize `ScanId`/`Aborted` transitions.
- `USER_SCAN_CONTEXT` stores the scanner’s worker context array, abort listener thread handle, finalize flag, scan connection port, and IO completion port.

## Dependencies And Usage

- `userscan.c` owns allocation and lifetime of the worker context array and thread handles.
- Callers must provide a writable `USER_SCAN_CONTEXT`, call `UserScanInit()` after the minifilter is loaded, and call `UserScanFinalize()` before normal scanner exit.
- The header is user-mode only; it depends on Filter Manager user-mode communication APIs through `fltUser.h`.

## Risks And Invariants

- `USER_SCAN_CONTEXT` has no constructor or zeroing helper; callers are expected to initialize or provide clean storage before `UserScanInit()`.
- `Finalized` is a plain `BOOLEAN`; `userscan.c` treats it as cross-thread state without interlocked access.
