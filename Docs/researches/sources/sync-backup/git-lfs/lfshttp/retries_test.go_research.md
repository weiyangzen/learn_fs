# sources/sync-backup/git-lfs/lfshttp/retries_test.go

Purpose: Tests request retry annotation and body replay after transient network failures.

Important APIs/types/functions: Exercises `WithRetries`, `Retries`, `Client.Do`, and `MarshalToRequest`.

Control flow: The retry integration test runs a server that hijacks and closes the first two connections, then returns success on the third request. The client sends a JSON POST with retry count high enough to succeed.

State and persistence behavior: Uses atomic request counter and in-memory request context. The seekable body is rewound between failed attempts.

Dependencies and integration points: Integrates retry context with `DoWithRedirect`, request tracing, and `httptest` raw connection hijacking.

Risks and edge cases: Test skips if the server cannot hijack raw connections. It verifies body replay but not retry exhaustion error shape.

Test signals: Strong signal that retries preserve JSON body content across network-level failures.
