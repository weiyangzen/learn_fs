# sources/sync-backup/git-lfs/lfshttp/stats.go

Purpose: Logs HTTP transfer timing and body-size statistics for requests and responses.

Important APIs/types/functions: `httpTransfer`, `LogHTTPStats`, `LogRequest`, `syncLogger`, `syncLogger.LogRequest`, `syncLogger.LogResponse`, `logTransfer`, and `Close`.

Control flow: `LogHTTPStats` writes a header and installs an async logger. `LogRequest` attaches `httptrace.ClientTrace` callbacks to a request context. Traced request/response bodies call logger methods from verbose tracing when bytes are read. `syncLogger` serializes log lines through a buffered channel and wait group.

State and persistence behavior: Writes log lines to the provided `io.WriteCloser`. Transfer timing state is in request context and updated atomically.

Dependencies and integration points: Integrated by `Client.LogRequest`, `verbose.go` traced bodies, and transfer code needing HTTP stats. Uses `httptrace`, atomics, and `UserAgent`.

Risks and edge cases: Response stats are emitted only when the response body reaches EOF. If callers do not drain/close bodies, response lines may be missing. The logger wait-group pattern requires `Close` for flush.

Test signals: `stats_test.go` covers enabled with key, enabled without request key, and disabled behavior.
