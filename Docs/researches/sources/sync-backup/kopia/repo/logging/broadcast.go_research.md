# sources/sync-backup/kopia/repo/logging/broadcast.go

Purpose: creates a logger that fans each zap log entry out to multiple underlying loggers.

Important APIs/types/functions: `Broadcast`, `Logger`, zap `Core`, and `zapcore.NewTee`.

Control flow: unwrap each sugared logger, collect its core, track a shared logger name when all inputs match or `-` when they differ, then build a new sugared logger over the tee core.

State/persistence behavior: no persistent state; it composes in-memory logging sinks.

Dependencies/integration: used by `WithAdditionalLogger` to attach secondary logging to an existing context without replacing the original logger.

Risks/test signals: passing zero loggers would create a tee with no cores. Tests verify fan-out and field formatting to two test loggers.
