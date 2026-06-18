# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/utility.c

## Purpose

Provides a user-mode diagnostic helper for translating Win32/HRESULT-style error codes into printable messages for the `avscan` user scanner.

## API Surface

- Implements `DisplayError(DWORD Code)` declared in `utility.h`.

## Control Flow

- Calls `FormatMessage(FORMAT_MESSAGE_FROM_SYSTEM)` first.
- If the system table does not contain the message, obtains the system directory, appends `\fltlib.dll`, loads it as a data file, and retries `FormatMessage(FORMAT_MESSAGE_FROM_HMODULE)`.
- Frees the message module if loaded and prints either the translated wide string or a fallback `Could not translate error` message.

## Dependencies

- Windows APIs: `FormatMessage`, `GetSystemDirectory`, `LoadLibraryExW`, `FreeLibrary`.
- String helper: `StringCchCat` from `<Strsafe.h>`.
- C runtime output: `printf`.

## Risks And Invariants

- Uses a `MAX_PATH` stack buffer and checks the system directory length before appending.
- The input parameter is named `Code` and typed as `DWORD`, but callers often pass `HRESULT` values; this matches the sample’s diagnostic needs because Filter Manager HRESULTs may be backed by `fltlib.dll` messages.
