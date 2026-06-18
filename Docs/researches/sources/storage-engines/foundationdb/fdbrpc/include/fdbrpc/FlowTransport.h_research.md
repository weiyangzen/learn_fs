# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/FlowTransport.h

## Purpose
`FlowTransport.h` declares the core fdbrpc transport interface: endpoint identity/serialization, message receivers, peer state, reliable/unreliable sending, endpoint registration, connection management, metrics, health, compatibility, peer trust, and public key support.

## Important APIs, Types, and Functions
Key types are `Endpoint`, `NetworkMessageReceiver`, `Peer`, `PeerCompatibilityPolicy`, and `FlowTransport`. Important APIs include endpoint construction/well-known tokens/serialization, `FlowTransport::createInstance`, `bind`, local address getters, peer reference management, endpoint registration/removal, `sendReliable`, `cancelReliable`, `sendUnreliable`, degraded/incompatible peer access, protocol-version async vars, `loadedEndpoint`, `loadedDisconnect`, `healthMonitor`, peer trust/current peer accessors, and public key load/watch methods.

## Control Flow
Endpoints carry address lists and tokens; deserialization adjusts primary address for TLS/secondary-address preferences. `FlowTransport` owns local endpoints and peers, binds listeners, sends packets reliably or unreliably, tracks peer references for streams and requests, and exposes transport-global state through `g_network`. `Peer` stores unsent/reliable queues, connection actors/triggers, ping/connect latency sketches, byte counters, compatibility state, and disconnect promise.

## State and Persistence Behavior
Transport state is process-global through `g_network`. Peer and endpoint state is in-memory: queues, counters, futures, protocol versions, health monitor, and public keys loaded from JWKS files. Public key files are read from disk by declared methods but key state is held in memory.

## Dependencies and Integration Points
It depends on `DDSketch`, `HealthMonitor`, Flow actors/network/protocol/packet/arena/public-key support, and `IPAllowList`. It is foundational for fdbrpc request/reply streams, failure monitoring, authorization, TLS address choice, and protocol compatibility.

## Risks and Edge Cases
Endpoint equality and hashing combine token and primary address, so address adjustment matters. Reliable packet lifetime must be explicitly cancelled. Compatibility and peer protocol state can change asynchronously. `Endpoint::isLocal` calls the global transport and requires an initialized instance. Public key file watching introduces filesystem and parsing failure modes in transport setup.

## Test Signals
Signals include transport unit/simulation tests for endpoint serialization, reliable delivery, missing/unauthorized endpoint handling, connection reset, incompatible peer tracking, peer metrics, and authorization token validation.
