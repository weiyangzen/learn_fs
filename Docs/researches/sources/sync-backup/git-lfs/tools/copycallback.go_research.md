<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/copycallback.go -->
# sources/sync-backup/git-lfs/tools/copycallback.go

Purpose: wraps readers/read-seek-closers to report copy progress through callbacks while preserving seek and close behavior.

Important APIs/types/functions: `CopyCallback`, `BodyWithCallback`, `NewByteBodyWithCallback`, `NewFileBodyWithCallback`, `NewBodyWithCallback`, `Read`, `Seek`, `ResetProgress`, `CallbackReader`, `ReadSeekCloser`, `NewByteBody`, `closingByteReader`, `NewFileBody`, and `closingFileReader`.

Control flow: `Read` delegates to the underlying reader, increments cumulative read size on positive reads, and calls the callback with total size, cumulative read, and bytes since last read when no error or EOF occurs. `Seek` updates tracked progress according to seek mode before delegating. `ResetProgress` reports a negative delta equal to consumed bytes. `CallbackReader` provides the same read-progress behavior for plain `io.Reader`.

State and persistence: tracks read progress in memory (`readSize`/`ReadSize`); does not persist data. File wrapper intentionally makes `Close` a no-op around an existing `*os.File`.

Dependencies and integration points: integrates with transfer progress meters, retry/seekable upload bodies, byte-backed test bodies, and file-backed readers.

Risks: callback errors replace read errors and can stop callers. `ResetProgress` assumes callback is non-nil and will panic if called without one. Seek bookkeeping trusts caller offsets and total size.

Test signals: `copycallback_test.go` covers callback invocation on underfilled EOF reads, cumulative byte counts, and seek offset tracking.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/tools/copycallback.go -->
