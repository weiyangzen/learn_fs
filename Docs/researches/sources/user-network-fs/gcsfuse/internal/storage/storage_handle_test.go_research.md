## sources/user-network-fs/gcsfuse/internal/storage/storage_handle_test.go

Purpose: Suite-level tests for storage handle construction, bucket handle lookup, HTTP/gRPC client option construction, HNS/zonal/Pirlo bucket routing, billing-project wrapping, auth error propagation, tracing, gRPC metrics, local socket binding, and custom retry selection.

Important APIs/types/functions: `StorageHandleTest`, `fakeStorageControlServer`, `mockStorageLayout`, `controlClientCallOptionsWithRetry`, and tests around `NewStorageHandle`, `BucketHandle`, `createHTTPClientHandle`, `createClientOptionForGRPCClient`, `CreateGRPCControlClient`, `lookupBucketType`, and `controlClientForBucketHandle`.

Control flow: setup creates a fake storage backend and mocked storage control client; individual cases mutate `StorageClientConfig`, construct handles or client options, then assert concrete wrappers and retry call-option choices. gRPC socket-address tests stand up a local control server and verify peer source address. Bucket type tests mock `GetStorageLayout` responses and inspect inferred `gcs.BucketType`.

State and persistence behavior: mostly in-memory tests, but they temporarily mutate environment variables such as `GOOGLE_CLOUD_ENABLE_DIRECT_PATH_XDS` and global OpenTelemetry providers. The suite calls `fakeStorage.ShutDown()` in teardown and uses local listeners that must be stopped to avoid leakage.

Dependencies and integration points: depends on `cfg`, `gcs`, `storageutil`, fake storage helpers, testify suites/mocks, Google Storage Control v2 clients, gRPC, and OpenTelemetry SDKs. It verifies the public behavior of internal storage client wiring rather than only isolated helper functions.

Risks: broad setup means tests can become brittle when generated Google clients change call-option defaults. Auth tests rely on fixture service-account JSON and invalid token/key paths. Environment/provider mutation needs cleanup discipline. The mocked Pirlo layout still has a TODO for native Pirlo storage-layout responses.

Test signals: high-value coverage for auth success/failure, custom endpoints, anonymous access, Google library auth on/off, read-stall retry validation, direct-path env cleanup, billing project wrappers, zonal/non-zonal retry strategy, tracing option count, and local socket binding for both HTTP and gRPC.
