# sources/sync-backup/kopia/internal/contentlog/contentlog_logger.go

Purpose: provides strongly typed JSON content logging with context params, logger-level params, generic entries, and low allocation message helpers.

Important APIs/types/functions: `WriterTo`, `Logger`, `OutputFunc`, `Emit`, `Log`, `Log1` through `Log6`, `WithParams`, `NewLogger`, `RandomSpanID`, `HashSpanID`, and `debugMessageWithParams`.

Control flow: `Emit` returns early for nil logger/output, gets a pooled `JSONWriter`, writes object start, timestamp `t`, logger params, context params from a private context key, entry fields, newline, and sends the buffer to output. `LogN` helpers instantiate generic message structs with void params for unused slots.

State and persistence behavior: logger stores immutable params, output callback, and a time function defaulting to `clock.Now`. Context params are copied/appended when nested. Span IDs are random 5-byte base32 or SHA-256-derived base32 prefixes.

Dependencies/integration: used by epoch manager and other structured logging code; integrates `logparam` and `contentparam`.

Risks/test signals: output callback receives a pooled buffer slice; it must copy if retaining asynchronously. `rand.Read` errors are ignored. Tests cover nil handling, param ordering/content, custom entries, multiple newline-delimited records, errors, and span ID shape indirectly.
