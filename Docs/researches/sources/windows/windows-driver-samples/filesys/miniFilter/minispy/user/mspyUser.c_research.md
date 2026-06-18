# File Research: sources/windows/windows-driver-samples/filesys/miniFilter/minispy/user/mspyUser.c

Main MiniSpy user-mode control utility.

Key responsibilities:
- Connects to `\\MiniSpyPort`.
- Creates shared `LOG_CONTEXT`, a shutdown semaphore, and the log retrieval thread.
- Supports startup and interactive commands for attach, detach, list, screen logging, file logging, and exit.
- Lists current filter attachments across volumes.
- Translates Win32 and fltlib error codes into readable messages.

Command behavior:
- `/a <drive>` attaches the `MiniSpy` filter with `FilterAttach` and prints the created instance name.
- `/d <drive> [instance id]` detaches one instance with `FilterDetach`.
- `/l` lists volumes and attachment status.
- `/s` toggles screen logging after command mode exits.
- `/f <file>` toggles file logging.
- `go` / `g` exits command mode; `exit` terminates the program.

Important behavior:
- Logging to screen is disabled while in command mode, then restored according to `NextLogToScreen`.
- `ListDevices` enumerates filter volumes, maps volume names to DOS names, and calls `IsAttachedToVolume` for each.
- `IsAttachedToVolume` enumerates instances per volume and counts those whose filter name equals `MiniSpy`.
- Cleanup sets `CleaningUp`, waits for the logging thread to release the shutdown semaphore, closes file/port/thread/semaphore handles.

Dependencies and risks:
- Depends on `fltUser.h` volume/instance APIs and `mspyLog.c` for log retrieval.
- Command parsing is space-delimited and fixed-buffer based; there is no quoting support for file names with spaces.
- The `/f` path sets `LogToFile` after `fopen_s` even if the open fails in non-debug builds, which is sample-quality error handling.
