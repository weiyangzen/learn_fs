## sources/user-network-fs/gcsfuse/internal/logger/legacy_logger.go

### Purpose
`legacy_logger.go` bridges the package's `slog` logging system to the standard-library `log.Logger` API for dependencies that still require legacy loggers, especially `jacobsa/fuse`.

### Important APIs, Types, And Functions
The file exposes `NewLegacyLogger(level slog.Level, prefix, fsName string) *log.Logger`. It builds a handler from `defaultLoggerFactory`, adds mount attributes via `loggerAttr`, creates an `slog.NewLogLogger`, and resets the package logging level.

### Control Flow
When called, it creates a handler with the shared `programLevel` and prefix, attaches mount instance metadata, converts it to a legacy logger at the supplied slog level, then calls `setLoggingLevel(defaultLoggerFactory.level)` to keep global filtering aligned with current config.

### State, Persistence, And Dependencies
It reads and reuses global logger factory state and global mount ID behavior. There is no direct persistence. Dependencies are `log`, `log/slog`, and helpers from `logger.go`/`slog_helper.go`.

### Integration Points
This is a compatibility layer for third-party libraries that cannot yet accept `slog.Logger`. It preserves gcsfuse formatting, severity naming, prefixing, and mount-id attributes.

### Risks
Because it depends on global logger factory state, calls before logger initialization or during tests that mutate globals can affect output. The file is marked temporary, so new code should prefer native package logging functions.

### Test Signals
No direct legacy logger tests are present, but logger formatting tests indirectly cover the handler behavior it uses. A direct test would verify prefix, mount-id, and severity filtering through `log.Logger.Print`.
