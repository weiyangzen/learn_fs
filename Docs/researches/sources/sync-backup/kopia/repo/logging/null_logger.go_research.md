# sources/sync-backup/kopia/repo/logging/null_logger.go

Purpose: provides the package no-op logger and factory.

Important APIs/types/functions: `NullLogger` and `getNullLogger`.

Control flow: `NullLogger` is a sugared no-op zap logger; `getNullLogger` ignores the module and returns it.

State/persistence behavior: global immutable logger instance; no persistence.

Dependencies/integration: used as the default for contexts without logging and when `WithLogger` receives nil.

Risks/test signals: because no-op logging hides output, missing context may make debugging harder. Tests in `logging_test.go` verify null module behavior.
