# sources/storage-engines/foundationdb/fdbserver/mocks3/MockS3ServerChaos.cpp

## Purpose
Implements a chaos-injecting HTTP wrapper around `MockS3Server` for simulation tests that need S3 latency, throttling, server/auth errors, and response corruption.

## Important APIs, Types, And Functions
Private helpers include `registeredMockS3ChaosServers()`, `classifyS3Operation()`, `getOperationMultiplier()`, `generateS3ErrorXML()`, `maybeInjectDelay()`, `maybeInjectError()`, and `maybeCorruptResponse()`. `MockS3ChaosServerImpl::handleRequest()` is the core wrapper. Public functions include `clearMockS3ChaosRegistry()`, `MockS3ChaosRequestHandler::handleRequest()`, `clone()`, internal `registerMockS3ChaosServer()`, and `startMockS3ServerChaos()`.

## Control Flow
For each request the chaos server classifies the method/resource into read, write, delete, list, or multipart, optionally delays based on `S3FaultInjector`, optionally returns a throttling or weighted HTTP error XML response, delegates normal processing to `processMockS3Request()`, and optionally corrupts a successful response by replacing its ETag. Startup requires simulated network mode, deduplicates address registration in a static set, ensures mock S3 persistence is enabled/loaded, registers an HTTP handler with the simulator, and calls `initializeMockS3Persistence()`.

## State And Persistence Behavior
The chaos layer stores only a process-static set of registered chaos server addresses. Persistent object and multipart state is delegated to `MockS3Server.cpp`; chaos startup explicitly enables/loads it before and after registration to avoid request races.

## Dependencies And Integration Points
Depends on `MockS3ServerChaos.h`, `MockS3Server.h`, `ChaosMetrics`, simulator HTTP registration, Flow tracing, deterministic random, and `S3FaultInjector`. It integrates with S3 blob-store simulation workloads by replacing the normal mock S3 server endpoint with a chaos endpoint.

## Risks And Edge Cases
Operation classification is heuristic: PUT/POST with `"uploads"` in the resource are multipart, while other unrecognized verbs default to read. `maybeInjectError()` applies an error-rate gate and then another random check for general errors, so effective general error probability is lower than a naive reading of the configured rate. Corruption only changes ETag headers on successful responses and does not mutate payload bytes. Clearing the registry in production simulation can desynchronize it from simulator HTTP handler state.

## Test Signals
Signals include trace events `MockS3ChaosDelay`, `MockS3ChaosThrottle`, `MockS3ChaosError`, `MockS3ChaosCorruption`, and chaos metrics counters `s3Throttles`, `s3Errors`, `s3Corruptions`. S3 chaos workloads and retry/error-handling simulation tests are the main validation path.
