# sources/distributed-fs/tahoe-lafs/src/allmydata/windows/fixups.py

## Purpose
This Windows-only helper performs one process-level startup fix: suppressing critical-error and open-file error dialogs so Tahoe-LAFS command-line or service usage does not block on GUI prompts when Windows encounters removable media or file-association problems.

## Important APIs, Types, and Functions
`initialize()` is the sole public function. It checks platform and an internal `_done` flag, then calls `win32api.SetErrorMode` with `SEM_FAILCRITICALERRORS | SEM_NOOPENFILEERRORBOX`. The module-level `assert sys.platform == "win32"` exists to help mypy and to make accidental non-Windows import fail early.

## Control Flow
On Windows, import loads `win32api` and `win32con`. `initialize()` is idempotent: if the platform is not `win32` or `_done` is already true, it returns `True`; otherwise it sets `_done` before applying the error mode. Setting `_done` before the Win32 call prevents repeated attempts if callers retry after partial initialization.

## State and Persistence
The `_done` module global tracks whether initialization has run in the current process. `SetErrorMode` mutates process-wide Windows error handling state; it is not file-backed and does not survive process exit.

## Dependencies and Integration Points
Depends on pywin32's `win32api` and `win32con`. Callers must import it only on Windows or tolerate import failure. It is a startup/runtime integration helper rather than business logic.

## Risks and Test Signals
The process-global setting can affect all loaded libraries in the process. Tests should verify idempotence, non-Windows avoidance by callers, and that `SetErrorMode` receives exactly the combined flag value. Because import itself asserts Windows, cross-platform tests should mock or gate imports.
