# sources/storage-engines/foundationdb/fdbserver/networktest.cpp

Purpose: implements Flow/FDB network benchmark and diagnostic tests. It provides RPC-style ping/reply tests, streaming reply tests, a nanosleep latency probe, and peer-to-peer socket throughput/session tests exposed as unit-test style commands.

Important APIs and functions: `NetworkTestInterface` binds a well-known endpoint token. `NetworkTestServer` and `NetworkTestStreamingServer` serve request/reply and reply-stream traffic. `networkTestClient`, `testClient`, `testClientStream`, and `logger` drive concurrent clients and latency statistics. `RandomIntRange` parses fixed or min:max command parameters. `P2PNetworkTest` owns listeners, remote addresses, session counters, message framing, `readMsg`, `writeMsg`, `doSession`, `incoming`, `outgoing`, and `run`/`run_oneshot`. Test cases are `:/network/p2ptest` and `:/network/p2poneshottest`.

Control flow, state, and persistence: all state is process-local counters, latency accumulators, sockets, and actor collections. No durable state is written. P2P sessions use an int length header followed by payload bytes, explicitly run Flow handshakes, and update byte/session/error counters before periodic status logging.

Dependencies and integration: depends on Flow networking (`IConnection`, `INetworkConnections`, endpoints, actors), `NetworkTest.h` request types, `FLOW_KNOBS`, and unit-test registration. It integrates with external `fdbserver` network-test invocations rather than production transaction paths.

Risks and test signals: risks are measurement skew from shared non-atomic counters, unbounded loops in nanosleep and server modes, malformed length headers, and random remote selection with empty remote lists. Test signals are successful P2P handshakes, expected streaming indexes ending with `end_of_stream`, stable throughput output, and TraceEvents for connect, accept, or session errors.
