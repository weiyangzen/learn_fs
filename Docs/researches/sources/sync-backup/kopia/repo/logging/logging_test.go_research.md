# sources/sync-backup/kopia/repo/logging/logging_test.go

Purpose: validates logger fan-out, writer formatting, null/default logger behavior, additional logger composition, and benchmark overhead.

Important APIs/types/functions: `TestBroadcast`, `TestWriter`, `TestNullWriterModule`, `TestNonNullWriterModule`, `TestWithAdditionalLogger`, and `BenchmarkLogger`.

Control flow: tests create in-memory buffers or printf-style test loggers, emit debug/info/warn/error entries, and compare exact output order/content.

State/persistence behavior: no persistent state; tests operate on in-memory buffers and contexts.

Dependencies/integration: uses `internal/testlogging`, `logging.ToWriter`, `logging.WithLogger`, `logging.WithAdditionalLogger`, and `logging.Module`.

Risks/test signals: exact string assertions catch encoder changes. They also document that default background contexts use a no-op logger.
