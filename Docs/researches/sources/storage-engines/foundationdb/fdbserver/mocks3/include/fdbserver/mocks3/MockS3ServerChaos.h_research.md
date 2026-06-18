# sources/storage-engines/foundationdb/fdbserver/mocks3/include/fdbserver/mocks3/MockS3ServerChaos.h

## Purpose
Declares the chaos-enabled mock S3 server interface and documents its configuration philosophy for FoundationDB simulation testing.

## Important APIs, Types, And Functions
`S3Operation` categorizes requests as `READ`, `WRITE`, `DELETE`, `LIST`, or `MULTIPART`. `MockS3ChaosRequestHandler` implements `HTTP::IRequestHandler` with reference counting and an atomic destruction guard. Public functions are `startMockS3ServerChaos()` and `clearMockS3ChaosRegistry()`.

## Control Flow
Simulation tests configure `S3FaultInjector` rates/multipliers, start a chaos server at a `NetworkAddress`, and point S3 blob-store clients at that endpoint. The request handler delegates to `MockS3ServerChaos.cpp`, which injects faults before/after base mock S3 processing.

## State And Persistence Behavior
This header owns no state. The implementation keeps a chaos registration set, uses `S3FaultInjector` and `ChaosMetrics` globals, and delegates persistence to the base mock S3 server.

## Dependencies And Integration Points
Depends on Flow futures/network and `fdbrpc/HTTP`. The comments describe integration with `S3BlobStoreEndpoint`, S3 client workloads, chaos metrics, and test configs such as S3 client workload with chaos.

## Risks And Edge Cases
The header notes that registry clearing is for testing/debugging only because simulator HTTP handler state persists. Fault injection has no master boolean; misconfigured per-rate settings can unintentionally target all operations or none. The operation enum must stay aligned with classification logic in the implementation.

## Test Signals
Signals are S3 chaos workloads, retry/error-handling behavior, and chaos metrics/traces for injected S3 errors, throttles, delays, and corruptions.
