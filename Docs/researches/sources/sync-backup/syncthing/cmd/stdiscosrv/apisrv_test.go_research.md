# sources/sync-backup/syncthing/cmd/stdiscosrv/apisrv_test.go

Purpose: validates discovery API address normalization and retry-after behavior, plus a request benchmark.

Important APIs/tests: `TestFixupAddresses`, helper `addr`, `TestRetryAfterSHistogram`, and `BenchmarkAPIRequests`.

Control flow and state: fixup tests supply announced addresses with unspecified, loopback, multicast, IPv4/IPv6, and zero-port cases against synthetic remote addresses. Retry tests exercise `retryAfterTracker.retryAfterS` enough times to validate generated delays stay within configured bounds and cluster around the desired delay. The benchmark drives API request handling against an in-memory setup.

Dependencies/integration: uses `net`, `testing`, and local API helpers. It indirectly documents reverse-proxy derived remote IP/port semantics.

Risks and test signals: strong signal for address sanitation and deduplication, especially replacing `0.0.0.0`/`[::]` with the remote IP. Missing coverage remains for parsing proxy certificate headers, compression response behavior, database merge side effects, and GET not-found status classes.
