# sources/sync-backup/kopia/internal/repodiag/log_manager.go

Purpose: captures repository diagnostic logs into encrypted blobs and optional text output.

Important APIs/types/functions: `LogManager`, `NewLogger`, `Enable`, `Disable`, `outputEntry`, `flushNextBuffer`, `Sync`, `initNewBuffer`, `NewLogManager`, and `LogBlobPrefix`.

Control flow: log entries are written to a current gather buffer when enabled. Buffer size or sync triggers rotate the buffer, enqueue encrypted blob writes through `BlobWriter`, and optionally mirror entries to a text writer. `Sync` flushes the current buffer and waits for pending blob writes.

State and persistence behavior: maintains enabled flag, active buffer, blob sequence IDs, and pending async writes; log data persists as encrypted blobs.

Dependencies and integration points: integrates `contentlog.Logger`, repository diagnostic blob writer, and notification/logging code.

Risks and test signals: concurrency around buffer rotation and context cancellation is sensitive. Tests cover enabled logging, auto-flush, disabled mode, canceled context, and null writer behavior.
