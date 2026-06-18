# sources/sync-backup/git-lfs/lfshttp/verbose_test.go

Purpose: Tests verbose HTTP logging output, body filtering, and Authorization redaction controls.

Important APIs/types/functions: Exercises `Client.Do`, `MarshalToRequest`, `traceRequest`, `traceResponse`, `traceHTTPDump`, and `isTraceableContent`.

Control flow: Test servers validate requests and return JSON or binary responses. Tests configure `Verbose`, `VerboseOut`, and `DebuggingVerbose`, then inspect emitted dump strings.

State and persistence behavior: Uses in-memory output buffers and temporary test servers. No persistent state.

Dependencies and integration points: Validates interaction with JSON request bodies, response body draining, and HTTP dump formatting.

Risks and edge cases: Confirms Basic auth is redacted by default and visible only in debugging verbose mode. Confirms binary request/response body bytes are not printed.

Test signals: Strong coverage for user-visible verbose output. It does not test non-seekable body error handling.
