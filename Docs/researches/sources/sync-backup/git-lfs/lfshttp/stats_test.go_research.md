# sources/sync-backup/git-lfs/lfshttp/stats_test.go

Purpose: Tests HTTP stats logging header, request/response log lines, and disabled no-op behavior.

Important APIs/types/functions: Exercises `LogHTTPStats`, `LogRequest`, `Client.Do`, `syncLogger.Close`, and `nopCloser`.

Control flow: Test servers accept JSON POSTs, clients optionally enable logging, requests optionally carry a stats key, and tests drain response bodies before closing the client to flush logs.

State and persistence behavior: Logs write to in-memory buffers. Atomic server counters verify request counts.

Dependencies and integration points: Validates interplay between stats tracing, verbose traced response body wrapping, and JSON request body marshaling.

Risks and edge cases: Confirms no per-request lines are emitted without `LogRequest` key/context, only the header. Disabled logging leaves `LogStats` empty.

Test signals: Good coverage of log shape and flush behavior. Does not assert exact timing values.
