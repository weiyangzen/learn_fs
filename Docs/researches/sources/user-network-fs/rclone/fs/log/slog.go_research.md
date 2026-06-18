# sources/user-network-fs/rclone/fs/log/slog.go

## Purpose
`slog.go` implements rclone's custom `log/slog` handler. It preserves rclone's historical text log format while also supporting JSON output, dynamic level changes, caller detection, extra destinations, and handler overrides for syslog/systemd/Event Log integration.

## Important APIs, types, and functions
Key exports are global `Handler`, `OutputHandler`, `NewOutputHandler`, and methods `SetOutput`, `ResetOutput`, `AddOutput`, `SetLevel`, `Enabled`, `Handle`, `WithAttrs`, and `WithGroup`. Important helpers include `defaultHandler`, `slogLevelToString`, `mapLogLevelNames`, `isLogFrame`, `getCaller`, `formatStdLogHeader`, `textLog`, and `jsonLog`.

## Control flow
`defaultHandler` creates a stderr handler and installs it into `fs.SetLogger` without changing process default slog. `Handle` snapshots format flags, builds text and/or JSON buffers depending on main and extra outputs, then writes to the override output stack or base writer and mirrors to extra destinations. Text formatting builds date/time/microsecond/UTC/file/PID/level/object prefixes. JSON formatting adds source and optional PID attributes.

## State and persistence behavior
`OutputHandler` stores writer, format flags, level variable, override stack, extra outputs, mutex, JSON buffer, and JSON handler. All mutable handler state is protected by `mu`. Persistence depends on the writer/output functions supplied by `InitLogging`.

## Dependencies and integration points
Core `fs/log.go` sends records to this handler. `log.go` mutates `Handler` during `InitLogging`; syslog/systemd/Event Log files use `SetOutput` or `AddOutput`. The handler implements `slog.Handler` for standard library compatibility.

## Risks and edge cases
Caller detection must skip rclone and standard-library logging frames, including `-trimpath` paths. `WithAttrs` and `WithGroup` intentionally ignore attrs/groups, which may surprise generic slog users. JSON and text buffers are both built when different destinations need different formats. Incorrect locking could deadlock under concurrent logging and reconfiguration.

## Test signals
`slog_test.go` covers level-name mapping, attr replacement, caller-frame skipping, text header variants, level enabling, format flag mutation, output override/reset, extra text/JSON outputs, JSON PID, handler cloning, direct text/JSON generation, concurrent reconfiguration/logging, and JSON-versus-text handling.

Source-read signal: reviewed complete local file (439 lines). Types observed: `OutputHandler`, `outputExtra`, `outputFn`. Functions/methods observed: `defaultHandler`, `slogLevelToString`, `mapLogLevelNames`, `isLogFrame`, `getCaller`, `getFormat`, `NewOutputHandler`, `SetOutput`, `ResetOutput`, `AddOutput`, `SetLevel`, `setWriter`, `setFormat`, `clearFormatFlags`, `setFormatFlags`, `Enabled`.
