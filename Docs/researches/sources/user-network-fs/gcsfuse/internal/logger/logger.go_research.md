## sources/user-network-fs/gcsfuse/internal/logger/logger.go

### Purpose
`logger.go` centralizes gcsfuse logging configuration, global logger state, mount-instance IDs, severity-filtered formatted logging helpers, file/syslog output, and fatal exit behavior.

### Important APIs, Types, And Functions
Constants include `ProgramName`, `GCSFuseInBackgroundMode`, `MountUUIDEnvKey`, `MountIDKey`, and `mountUUIDLength`. Public functions include `InitLogFile`, `MountUUID`, `MountInstanceID`, `UpdateDefaultLogger`, `Tracef`, `Debugf`, `Infof`, `Info`, `Warnf`, `Errorf`, `Error`, `GetLogFHandler`, `Fatal`, and `SetOutput`. `loggerFactory` creates text or JSON handlers and chooses file, syslog, or stdout writers.

### Control Flow
Package init seeds a default stdout logger from default config. `InitLogFile` opens a configured file and creates a lumberjack rotator, or creates a syslog writer when running in background mode without a file path. It then creates a logger with mount-id attributes. Mount UUID is lazily initialized once: background mode reads `GCSFUSE_MOUNT_UUID`, foreground mode generates an eight-character UUID prefix. Logging helper functions manually check `programLevel` before emitting records. `Fatal` logs an error, logs a stack trace, then exits.

### State, Persistence, And Dependencies
Global mutable state includes `defaultLoggerFactory`, `defaultLogger`, `mountUUID`, `setupMountUUIDOnce`, and `programLevel`. Persistent outputs are log files via `lumberjack`, syslog, or stdout. Dependencies include `slog`, `syslog`, `debug.Stack`, `uuid`, config types, and lumberjack rotation.

### Integration Points
Most internal packages use these logging helpers. Monitoring, kernelparams, perf, profiler, and locker code all depend on it. Mount-id attributes tie logs from a running filesystem instance to metrics/tracing identifiers.

### Risks
Global state makes tests and concurrent reconfiguration order-sensitive. `InitLogFile` opens an `os.File` just to obtain a path for lumberjack and retains it, so callers/tests must close it if they care about descriptors. `Fatal` is hard process exit. Unsupported log levels in `setLoggingLevel` leave the previous level unchanged.

### Test Signals
`logger_test.go` verifies text/JSON formatting across levels, file logger initialization, runtime format update, UUID generation, background/foreground UUID setup, and `GetLogFHandler`. Tests do not cover syslog creation, fatal exit, log rotation behavior, or concurrent reconfiguration.
