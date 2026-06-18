## sources/sync-backup/syncthing/lib/protocol/benchmark_test.go

Purpose: benchmarks BEP request throughput over loopback TCP, with and without TLS.

Important functions/types: `BenchmarkRequestsRawTCP`, `BenchmarkRequestsTLSoTCP`, `benchmarkRequestsTLS`, `benchmarkRequestsConnPair`, `getTCPConnectionPair`, `negotiateTLS`, and `fakeModel`. The fake model responds to requests with a buffer of requested size containing the offset encoded at the end.

Control flow and state: benchmarks create a connected TCP pair, optionally wrap it in TLS, start two protocol connections, send cluster configs, then alternate 128 KiB requests between both directions while verifying buffer length and offset marker.

Dependencies and integration points: uses protocol `NewConnection`, dialer TCP options, test certificates, compression metadata, and connection/model interfaces. It measures connection request/response performance rather than correctness of model storage.

Risks: TLS benchmark skips if test certificates are unavailable. Loopback performance depends on host and TCP settings. It uses `InsecureSkipVerify` appropriately for local benchmark setup.

Test signals: benchmark-only performance signal for raw and TLS request paths.
