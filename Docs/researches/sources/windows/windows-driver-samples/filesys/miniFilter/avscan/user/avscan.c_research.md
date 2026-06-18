# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/avscan/user/avscan.c

User-mode scanner entry point. It initializes user scan worker state, waits for interactive quit input, finalizes scanner resources, and exits.

Key behavior:
- Includes Windows, Filter Manager user API, shared AV protocol, user utility, and `userscan.h`.
- `main` ignores command-line arguments, zero-initializes `USER_SCAN_CONTEXT`, and calls `UserScanInit`.
- On initialization failure, it prints an error, calls `DisplayError`, and returns `255`.
- It loops prompting `press 'q' to quit:` and exits only when the user enters `q`.
- On exit, it calls `UserScanFinalize`; finalize failure is reported but does not change the returned status.
- Successful program exit returns `0`.

Dependencies:
- `UserScanInit`, `UserScanFinalize`, and `USER_SCAN_CONTEXT` are declared outside this file.
- Uses `fltUser.h` for user-mode Filter Manager communication support and `avlib.h` for shared protocol definitions.

Research notes:
- This file is only the console harness; scan worker behavior and message handling live in other user-mode files not included in this group.
