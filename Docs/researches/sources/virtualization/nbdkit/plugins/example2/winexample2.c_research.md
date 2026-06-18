# File Research: sources/virtualization/nbdkit/plugins/example2/winexample2.c

Windows version of the example2 read-only file-serving plugin.

Key behavior:
- Requires Windows build and errors if compiled elsewhere.
- Requires `file=<filename>`, resolved with `nbdkit_realpath`.
- Opens with `CreateFile` for shared read access.
- Stores `HANDLE` in the per-connection handle.
- Uses `GetFileSizeEx` for size.
- Uses `ReadFile` with an `OVERLAPPED` offset for positional reads.
- Closes with `CloseHandle`.

Differences from POSIX example:
- Windows API error reporting uses `GetLastError`.
- No explicit errno preservation flag in the plugin registration.
- Does not loop to verify short reads; it relies on `ReadFile` behavior for the example.
