# sources/storage-engines/foundationdb/fdbrpc/SimExternalConnection.cpp

## Purpose
`SimExternalConnection.cpp` implements an `IConnection` adapter that lets simulated FoundationDB processes connect to real TCP endpoints through Boost.Asio. It is used for external-client style simulation tests, DNS resolution tests, and hostname resolution behavior while preserving Flow `Future` APIs.

## Important APIs, Types, and Functions
The file defines a static Boost `io_service`, `SimExternalConnectionImpl::connect`, `SimExternalConnectionImpl::onReadable`, all `SimExternalConnection` `IConnection` overrides, blocking and asynchronous `resolveTCPEndpoint` helpers, and three unit tests: `fdbrpc/SimExternalClient`, `fdbrpc/MockDNS`, and `/fdbrpc/Hostname/hostname`. `forceLinkSimExternalConnectionTests` ensures the object file is linked for tests.

## Control Flow
`connect` jitter-delays, converts `NetworkAddress` to a Boost endpoint, synchronously connects a socket, and returns either an invalid reference or a `SimExternalConnection`. `write` sends packet bytes via `SendBufferIterator`, sleeps briefly, reads all currently available echoed bytes into `readBuffer`, and triggers waiters if the buffer was previously empty. `onReadable` waits for jitter and then blocks on `onReadableTrigger` only if the local buffer is empty. DNS resolution uses Boost resolver synchronously, converts IPv4/IPv6 endpoints to public `NetworkAddress` values, adds them to the DNS cache, and reports failures as `lookup_failed`.

## State and Persistence Behavior
Connection state is per object: a Boost TCP socket, debug UID, a deque-backed read buffer, and an async readable trigger. DNS state is persisted only in the provided `DNSCache` and in mock endpoint registrations owned by `INetworkConnections`. There is no durable storage.

## Dependencies and Integration Points
The implementation depends on Boost.Asio, `flow/IConnection.h`, `flow/Net2Packet.h`, `SendBufferIterator`, `Hostname`, `UnitTest`, and `INetworkConnections::net()`. It integrates with simulation by providing a real external connection implementation and mock DNS handling inside the network abstraction.

## Risks and Edge Cases
Most socket operations are synchronous and can block the simulation thread. `write` assumes data becomes readable after a fixed `threadSleep(0.1)` and asserts on errors, making it test-oriented rather than production tolerant. `hasTrustedPeer` always returns true, which is appropriate for this test adapter but bypasses peer-auth semantics. The test echo server binds a fixed port `8000`, so parallel runs or occupied ports can fail.

## Test Signals
`fdbrpc/SimExternalClient` starts a local echo server, connects through `INetworkConnections`, writes random bytes, reads the echo, and asserts equality. `fdbrpc/MockDNS` verifies mock endpoint add/remove behavior. The hostname test verifies async, blocking, and retry resolution against a mock endpoint in simulation.
