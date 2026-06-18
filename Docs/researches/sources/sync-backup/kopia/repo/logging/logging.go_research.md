# sources/sync-backup/kopia/repo/logging/logging.go

Purpose: defines the repository logging abstraction over zap and helpers for module loggers and writer-backed test/debug loggers.

Important APIs/types/functions: `Logger`, `LoggerFactory`, `Module`, and `ToWriter`.

Control flow: `Module` returns a closure that pulls the cached logger factory from context and falls back to `NullLogger`. `ToWriter` builds a zap core with Kopia's standard console encoder and debug level, returning its `.Named` function as a module factory.

State/persistence behavior: no persistence; the context selects log sinks dynamically.

Dependencies/integration: depends on zap, zapcore, and `internal/zaplogutil`. Most repository packages define module loggers using this file.

Risks/test signals: missing context silently drops logs via null logger. Tests verify writer formatting and module lookup behavior.
