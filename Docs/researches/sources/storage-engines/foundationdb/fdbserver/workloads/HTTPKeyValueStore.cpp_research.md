# sources/storage-engines/foundationdb/fdbserver/workloads/HTTPKeyValueStore.cpp

## Purpose
Simulation workload that tests the Flow HTTP client and simulated HTTP server path with a simple per-client key-value service. It exercises name resolution, connection reuse, request retries, header/content validation, and response integrity.

## Important APIs, types, and functions
`SimHTTPKVStore` stores string data and per-client sequence numbers. `httpKVRequestCallback`, `httpKVProcessPut`, and `httpKVProcessGet` implement the server contract. `KeyValueRequestHandler` adapts the store to `HTTP::IRequestHandler`. `HTTPKeyValueStoreWorkload` uses `INetworkConnections`, `HTTP::doRequest`, `PacketWriter`, `UnsentPacketQueue`, `IncomingResponse`, and counters for gets, puts, connects, and failed connects.

## Control flow
Client 0 registers a simulated server at `httpkvstore:80`; every client then preloads `nodeCount` keys through HTTP PUT. `doKVRequest` creates or reconnects a connection, optionally manually resolves endpoints, builds headers (`Key`, `ClientID`, `UID`, `SeqNo`), sends PUT or GET, validates echoed headers, and retries only timeout/connect/lookup failures. The start phase runs random GET/PUT traffic at a Poisson rate; check cancels the client and reads all keys back.

## State and persistence behavior
No FoundationDB keys are used. Persistent test state is the process-global `globalKVStore` map inside simulation and each workload instance's `myData` mirror plus `activePut`. Sequence numbers suppress out-of-order retransmits, and `activePut` permits a check to accept either the old local value or the in-flight PUT value if cancellation interrupted a write.

## Dependencies and integration points
Requires simulated networking and `g_simulator->registerSimHTTPServer`. It integrates with Flow HTTP serialization, connection handshake and close paths, DNS resolution, MD5 response headers, and tester workload metrics.

## Risks and test signals
Risks include strict header-count assertions, `opsPerSecond` accidentally reading the `nodeCount` option, process-global state coupling across handler clones, and no server-side missing-key handling beyond ASSERT. Signals are ASSERTs on HTTP codes, content length, echoed headers, MD5-bearing GET responses, local mirror consistency, and perf counters for request/connect behavior.
