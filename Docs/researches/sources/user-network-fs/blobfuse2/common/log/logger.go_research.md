# sources/user-network-fs/blobfuse2/common/log/logger.go
## sources/user-network-fs/blobfuse2/common/log/logger.go

Purpose: exposes the package-level logging facade and logger factory used across blobfuse2.

Important APIs/types/functions: `Logger` interface, `NewLogger`, global `logObj`, global `timeTracker`, getters, `SetDefaultLogger`, `SetConfig`, setters, `Destroy`, level functions `Debug`/`Trace`/`Info`/`Warn`/`Err`/`Crit`, `LogRotate`, `TimeTrack`, and `TimeTrackDiff`.

Control flow: `NewLogger` chooses `base`, `silent`, or `syslog`/default. Syslog creation falls back to base logging only for `ErrNoSyslogService`. `SetDefaultLogger` replaces global `logObj`. `SetConfig` mutates the current logger's file, level, max size, count, and time tracking. Package-level level functions delegate directly to `logObj`. `init` defaults to syslog with debug level, falling back internally if needed.

State and persistence: global logger instance and time-tracker flag are mutable process state. Depending on logger type, output may go to syslog, files, stdout, or nowhere.

Dependencies/integration: `BaseLogger`, `SilentLogger`, `SysLogger`, `common.LogConfig`, and `time`.

Risks: package-level logging functions panic if `logObj` is nil, though init normally sets it. Replacing loggers does not automatically destroy the previous logger. `SetConfig` on syslog silently ignores file/size/count settings. Time tracking logs at critical level, which may be surprising.

Test signals: `logger_test.go` covers base, silent, syslog/fallback, invalid logger type, level changes, and high-volume logging.
