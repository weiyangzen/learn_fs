# File Research: sources/windows/reactos/ntoskrnl/io/iomgr/bootlog.c

## Purpose

`bootlog.c` implements ReactOS boot driver logging. It records load success/failure entries under the registry during boot and can later write them to `\SystemRoot\rosboot.log`.

## State

- `IopBootLogCreate`: whether a log file should be created later.
- `IopBootLogEnabled`: whether registry boot logging is currently accepting entries.
- `IopLogFileEnabled`: set after log file save completes.
- `IopLogEntryCount`: numeric registry value index.
- `IopBootLogResource`: serializes boot-log registry/file operations.

## Main Functions

- `IopInitBootLog(BOOLEAN StartBootLog)` initializes the resource and optionally starts logging.
- `IopStartBootLog()` enables logging and requests later file creation.
- `IopStopBootLog()` disables accepting new boot-log entries.
- `IopBootLog(PUNICODE_STRING DriverName, BOOLEAN Success)`:
  - Returns immediately if logging is disabled.
  - Formats either "Loaded driver" or "Did not load driver" plus driver name.
  - Opens `\Registry\Machine\System\CurrentControlSet`.
  - Creates/opens the `BootLog` key.
  - Writes the entry as `REG_SZ` under a numeric value name.
  - Increments the entry count on success.
- `IopWriteLogFile(PWSTR LogText)` opens `\SystemRoot\rosboot.log` for append, writes optional text, then writes CRLF.
- `IopCreateLogFile()` supersedes `rosboot.log` and writes a UTF-16 BOM.
- `IopSaveBootLogToFile()` creates the file, writes an initial blank line, reads numeric registry values from `BootLog` until missing, appends each value to the file, deletes each registry value, and enables the log-file flag.

## Important Details

- Registry and file paths are kernel object-manager paths.
- File content is UTF-16 because it writes wide strings and starts with BOM `0xFEFF`.
- There is a locking issue in the current implementation: `IopSaveBootLogToFile()` acquires `IopBootLogResource` and calls `IopCreateLogFile()`, which also acquires the same resource without releasing it in that function. This is notable for deadlock/reentrancy review.

## Research Notes

This file is not a filesystem implementation, but it exercises kernel file creation/writes during boot and depends on the storage/filesystem stack becoming available enough for `\SystemRoot\rosboot.log`.
