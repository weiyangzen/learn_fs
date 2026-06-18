# sources/storage-engines/foundationdb/fdbserver/mocks3/include/fdbserver/mocks3/MockS3Server.h

## Purpose
Declares the public interface for the deterministic mock S3 server used by FoundationDB simulation and ctest HTTP scenarios.

## Important APIs, Types, And Functions
`MockS3RequestHandler` implements `HTTP::IRequestHandler` with `handleRequest()`, `clone()`, reference counting, and an atomic destruction guard. Public functions start/register the server, clear global storage, enable/check/load/initialize persistence, and process a request directly: `startMockS3Server()`, `startMockS3ServerReal()`, `clearMockS3Storage()`, `registerMockS3Server()`, `enableMockS3Persistence()`, `isMockS3PersistenceEnabled()`, `loadMockS3PersistedStateFuture()`, `initializeMockS3Persistence()`, and `processMockS3Request()`.

## Control Flow
Normal HTTP use constructs/clones `MockS3RequestHandler` and calls `handleRequest()`, which delegates to the implementation. Simulation callers usually call `registerMockS3Server()` or `startMockS3Server()`. Real ctest callers use `startMockS3ServerReal()`. Chaos code calls `processMockS3Request()` after injecting faults.

## State And Persistence Behavior
The header exposes controls for global in-memory storage and optional disk persistence, but state is implemented in `MockS3Server.cpp`. The destruction guard avoids handling or cloning while a handler is being destroyed.

## Dependencies And Integration Points
Depends on Flow futures/network and `fdbrpc/HTTP`. It is consumed by mock S3 implementation, chaos wrapper, simulator setup, S3 client workloads, and tests.

## Risks And Edge Cases
The direct request processor is low-level and assumes callers pass initialized HTTP request/response objects with usable content queues. Persistence APIs are global, so callers must be aware that state can span simulated processes and tests. `clone()` can return an empty reference during destruction.

## Test Signals
Signals include `fdbserver_mocks3_test`, simulation workloads using `registerMockS3Server()`, and chaos wrapper integration through `processMockS3Request()`.
