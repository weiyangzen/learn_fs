## sources/user-network-fs/gcsfuse/internal/logger/slog_helper.go

### Purpose
`slog_helper.go` adapts Go `slog` output to the gcsfuse log schema: custom severity names, custom message key, custom timestamp shape, optional prefixes, and package log-level filtering.

### Important APIs, Types, And Functions
It defines custom levels `LevelTrace` and `LevelOff` plus aliases for debug/info/warn/error. Internal helpers are `setLoggingLevel`, `customiseLevels`, `addPrefixToMessage`, `customiseTimeFormat`, and `getHandlerOptions`.

### Control Flow
`setLoggingLevel` maps config strings to `programLevel`. Handler options use `ReplaceAttr` to rename `level` to `severity`, convert custom level values to config strings, rename message to `message` while prepending a prefix, and convert time either to a formatted text string or to a JSON `timestamp` group with seconds and nanos.

### State, Persistence, And Dependencies
The file mutates the package-global `programLevel`. It persists only through emitted log records. Dependencies are `log/slog`, `strings`, `time`, and config constants.

### Integration Points
`loggerFactory` uses `getHandlerOptions` for both text and JSON handlers, and `NewLegacyLogger` reuses the same logic. This file defines the schema expected by tests and external logging systems such as FluentD.

### Risks
`customiseLevels`, `addPrefixToMessage`, and `customiseTimeFormat` type-assert attribute values; unexpected attribute shapes from future `slog` changes or custom records could panic. Unknown levels default to INFO label. Invalid config strings leave the previous `programLevel` unchanged.

### Test Signals
The logger tests validate the resulting schema, level names, timestamps, prefixes, and filtering. There are no direct unit tests for malformed attributes or invalid level strings.
