# sources/user-network-fs/blobfuse2/common/log/silent_logger.go
## sources/user-network-fs/blobfuse2/common/log/silent_logger.go

Purpose: implements a no-op logger that satisfies the `Logger` interface for tests or intentionally silent operation.

Important APIs/types/functions: `SilentLogger` and its methods `GetLoggerObj`, `GetType`, `GetLogLevel`, all severity methods, `LogRotate`, `Destroy`, and configuration setters.

Control flow: every logging/configuration method either returns a static value or does nothing. `GetType` returns `silent`, `GetLogLevel` returns `LOG_OFF`, `GetLoggerObj` returns nil, and error-returning methods return nil.

State and persistence: no state and no persistence.

Dependencies/integration: satisfies the `Logger` interface from `logger.go` and uses `common.LogLevel` constants.

Risks: callers that assume `GetLoggerObj()` is non-nil can panic when using silent logging. Configuration setters silently discard changes, which is intended but can hide mistaken logger selection.

Test signals: `logger_test.go` calls logging methods through the facade after selecting the silent logger and expects no error.
