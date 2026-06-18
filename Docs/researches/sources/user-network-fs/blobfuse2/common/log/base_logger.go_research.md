# sources/user-network-fs/blobfuse2/common/log/base_logger.go
## sources/user-network-fs/blobfuse2/common/log/base_logger.go

Purpose: implements asynchronous file/stdout logging with log levels and size-based rotation.

Important APIs/types/functions: `LogFileConfig`, `BaseLogger`, `newBaseLogger`, getter methods, level methods `Debug`/`Trace`/`Info`/`Warn`/`Err`/`Crit`, setters, `init`, `Destroy`, `logEvent`, `logDumper`, and `LogRotate`.

Control flow: initialization sets defaults for log file, level, size, and count, opens the file or stdout, creates a `log.Logger`, and starts a goroutine consuming a buffered channel of log strings. Each level method compares configured level and enqueues via `logEvent`, which formats timestamp, tag, pid, mount path, caller file/line, and optional goroutine ID. The dumper writes each message and triggers rotation when accumulated size exceeds the limit. Rotation closes the file, deletes the oldest numbered file, renames numbered files upward, renames current to `.1`, and opens a new file.

State and persistence: persists log files and rotated backups. Maintains current log size, file handle, logger, pid, channel, and worker wait group. `Destroy` closes the channel, waits, then closes the handle.

Dependencies/integration: `common.LogLevel`, `common.MountPath`, `common.GetGoroutineID`, filesystem, runtime caller info, and Go's `log` package.

Risks: channel buffer is large but sends can block under heavy logging. `SetLogFile` swaps file handles without closing the old one. `Destroy` closes stdout when logging to stdout. Rotation errors from remove/rename are ignored. Size accounting uses message length, not newline or actual bytes.

Test signals: `logger_test.go` stress logs enough messages to exercise rotation and `Destroy`.
