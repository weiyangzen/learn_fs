# sources/storage-engines/pebble/internal/base/error_test.go

Purpose: Tests corrupt block data attachment and extraction behavior.

APIs and types: Exercises `AttachCorruptBlockData`, `ExtractCorruptBlockData`, and `errors.Wrap` interaction.

Control flow and state: Creates a base error, attaches `[]byte("foo")`, wraps the error, then confirms extraction still finds the original data through the error chain.

Persistence and dependencies: No persistence. Depends on `cockroachdb/errors` and `testify/require`.

Integration points: Confirms corruption diagnostics survive the same wrapping style used by higher Pebble layers.

Risks: Narrow coverage: it does not test marker classification, nil errors, or mutation of attached data.

Test signals: Positive signal for wrapped-data extraction; broader error classification remains covered elsewhere or by integration tests.
