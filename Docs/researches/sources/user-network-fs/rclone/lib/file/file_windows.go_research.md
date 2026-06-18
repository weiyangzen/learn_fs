# sources/user-network-fs/rclone/lib/file/file_windows.go

Source read signal: reviewed complete local file (102 lines, sha256 59892294574fc74a).

Purpose: Windows implementation of file opening that allows open files to be renamed/deleted, plus Windows reserved-name validation.

Important APIs/types/functions: Exports `OpenFile` and `IsReserved`. `OpenFile` maps Go open flags to `syscall.CreateFile` access/create modes and includes `FILE_SHARE_DELETE`.

Control flow: `OpenFile` validates path, converts to UTF-16, computes access and create modes from flags, calls `CreateFile`, and wraps the handle with `os.NewFile`. `IsReserved` checks empty/current/separator-only paths, trailing spaces/periods, and DOS device basenames with a regexp.

State and persistence behavior: Opens or creates real files using Windows APIs. `IsReserved` is stateless.

Dependencies and integration points: Uses `syscall`, `os`, `filepath`, `regexp`, and Windows build tag. It underpins all package `Open`/`Create` calls on Windows.

Risks and test signals: Flag mapping must stay compatible with Go's `os.OpenFile` behavior while adding delete sharing. Reserved-name validation is basename-based and intentionally rejects `CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, and `LPT1-9` with extensions.
