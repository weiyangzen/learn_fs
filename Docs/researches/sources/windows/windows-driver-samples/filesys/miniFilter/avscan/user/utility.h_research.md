# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/utility.h

## Purpose

Declares the common user-mode error reporting helper used by the `avscan` scanner program.

## API Surface

- Includes `<windows.h>`.
- Declares `VOID DisplayError(_In_ DWORD Code);`.

## Dependencies And Usage

- Implemented by `utility.c`.
- Used by `userscan.c` on Filter Manager and Win32 error paths to print human-readable diagnostics.

## Risks And Invariants

- Header is minimal and user-mode specific.
- It exposes only diagnostics; it does not affect scanner protocol or lifecycle state.
