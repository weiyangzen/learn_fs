# sources/user-network-fs/blobfuse2/common/log/sys_logger.go
## sources/user-network-fs/blobfuse2/common/log/sys_logger.go

Purpose: implements syslog-backed logging for production/default logging paths.

Important APIs/types/functions: `SysLogger`, `ErrNoSyslogService`, `newSysLogger`, getters/setters, `init`, `getSyslogLevel`, `write`, severity methods, and no-op file/rotation methods.

Control flow: construction creates a syslog writer with a priority mapped from blobfuse log level and wraps it in a standard logger. Severity methods compare configured level and call `write`, which formats optional goroutine ID, mount path, severity, caller file/line, and message. `SetLogLevel` updates level and emits a critical reset message. File-oriented methods are no-ops because syslog manages persistence.

State and persistence: holds level, tag, goroutine-ID option, and syslog logger. Log records persist according to the host syslog service.

Dependencies/integration: Unix syslog, `common.LogLevel`, `common.MountPath`, `common.GetGoroutineID`, runtime caller info, and package factory fallback in `logger.go`.

Risks: syslog may be unavailable in containers or non-Unix environments; factory fallback handles only `ErrNoSyslogService`. The syslog priority is fixed at writer construction, so changing `level` later changes filtering but not the writer's facility/priority. Destroy/rotation do nothing.

Test signals: `logger_test.go` requests syslog and runs generic log calls, but it does not inspect syslog output.
