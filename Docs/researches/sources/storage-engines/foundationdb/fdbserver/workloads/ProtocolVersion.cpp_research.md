## sources/storage-engines/foundationdb/fdbserver/workloads/ProtocolVersion.cpp

`ProtocolVersionWorkload` checks simulator support for querying protocol information from a process running a different protocol version. It finds any simulator process whose `protocolVersion` differs from `currentProtocolVersion()`, sends a well-known `ProtocolInfoRequest`, and asserts the reply version differs from the current network protocol version.

Important APIs are `g_simulator->getAllProcesses`, `ISimulator::ProcessInfo::protocolVersion`, `currentProtocolVersion`, `Endpoint::wellKnown`, `WLTOKEN_PROTOCOL_INFO`, `RequestStream<ProtocolInfoRequest>`, and `retryBrokenPromise`.

The workload has no setup and no persistent state. `start` is the entire test: find the mixed-version process, assert one exists, build a request stream from that process address set, await the protocol info reply, and assert version mismatch. `check` returns true.

Risks are environmental: the workload requires a mixed-protocol simulation and will assert if none is present. It does not check process liveness beyond using `retryBrokenPromise`, and it validates only version inequality, not exact compatibility metadata. Integration is with simulator process metadata and the RPC well-known protocol-info endpoint. Test signals are the two assertions in `start`.
