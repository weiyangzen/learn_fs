# sources/object-store/apache-ozone/hadoop-hdds/client/src/main/java/org/apache/hadoop/hdds/scm/XceiverClientGrpc.java

Purpose: Standalone gRPC implementation of `XceiverClientSpi` for datanode container protocol operations, especially reads and non-Ratis standalone writes.

Important APIs/types/functions: Manages per-datanode `ManagedChannel` and async stubs in `ChannelInfo`. `connect`, `connectToDatanode`, and `createChannel` establish gRPC transport with optional TLS. `sendCommand`, `sendCommandAsync`, and `sendCommandOnAllNodes` send container protobuf requests. `sortDatanodes` chooses read retry order with leader/cache/topology/operational-state handling. Streaming read uses `initStreamRead`, `streamRead`, and `completeStreamRead`.

Control flow: Initial connect targets closest or first node. Each send injects trace ID and current client version if absent, then sends through a per-call gRPC bidirectional stream. A semaphore bounds outstanding requests, and metrics are incremented/decremented around each call. Synchronous sends retry datanodes in sorted order. `GetBlock` caches the successful datanode so `ReadChunk` can favor the same DN. EC requests are reconstructed with datanode UUID and replica index where needed.

State and persistence behavior: Holds pipeline, config, security config, metrics, timeout, semaphore, per-DN channel map, block-to-DN cache, trust manager, and closed flag. State is process-local and cleared on close.

Dependencies and integration points: Integrates with `XceiverClientManager` metrics, datanode protobuf service stubs, tracing, security/TLS, topology-aware reads, `HddsClientUtils`, and Ozone client versioning.

Risks: `pipeline.getNodes()` may return mutable lists; `sortDatanodes` swaps/shuffles returned lists, so pipeline list semantics matter. Semaphore release correctness depends on gRPC callbacks; streaming reads require explicit `completeStreamRead`. Close waits up to five seconds and logs unclosed channels. Authentication errors are translated to `SCMSecurityException`.

Test signals: Tests should cover datanode sort order, GetBlock/ReadChunk cache, EC request reconstruction, semaphore release on success/error, TLS/plaintext channel creation, close idempotence, and streaming read fallback.
