# sources/user-network-fs/gcsfuse/internal/storage/storage_handle.go

## Purpose
This file creates and manages storage clients and bucket handles. It selects HTTP, gRPC, or bidi gRPC transports, configures authentication, retries, DirectPath, metrics, control clients, billing project handling, and bucket type detection.

## Important APIs and Types
`StorageHandle` exposes `BucketHandle(ctx, bucketName, billingProject)`. `storageClient` stores HTTP, gRPC, bidi-gRPC, raw control clients with and without GAX retries, a wrapped control client, and `storageutil.StorageClientConfig`. Constants define hidden read-stall env vars, zonal location type, and DirectPath detection retry parameters.

## Control Flow
`createClientOptionForGRPCClient` builds gRPC/control client options: custom endpoint, anonymous/authenticated credentials, Google library auth or token source, bidi reads, local socket address dialer, tracing stats handler, connection pool, user agent, and metrics settings. `setRetryConfig` applies storage retry options using backoff and `storageutil.ShouldRetryWithMonitoring`. `createGRPCClientHandle` enables DirectPath env, builds a gRPC client with optional bidi config, enforces direct connectivity, verifies connectivity with a dummy stat, then applies production retry config. `verifyDirectPathConnectivity` temporarily disables Go SDK retries and accepts only not-found as a successful DirectPath proof. `createHTTPClientHandle` builds auth and HTTP client options, supports JSON reads, custom endpoints, read-stall retry hidden env vars, creates a storage client, and applies retries.

## State, Persistence, and Integration
`NewStorageHandle` optionally creates Storage Control clients when HNS is enabled and the endpoint is not localhost. It creates raw clients with and without default GAX retries, adds folder API retries, wraps layout calls with billing project and stall retry behavior, and stores config for lazy data-client creation. `lookupBucketType` calls `GetStorageLayout` and infers hierarchical, zonal, and Pirlo state. `getClient` chooses bidi gRPC for rapid buckets, non-bidi gRPC with HTTP fallback for gRPC protocol, or HTTP for HTTP protocols. `BucketHandle` combines bucket type, selected storage client, optional user project, appropriate control-client wrapper, bucket name, billing project, and write config into a `bucketHandle`.

## Dependencies and Risks
Dependencies include Google storage/data/control clients, experimental storage options, gax, cfg, logger, storageutil, local gcs errors, OpenTelemetry, OAuth2, gRPC, direct-path side-effect imports, and OS/env APIs. Major risks include process-wide environment mutation for DirectPath and read-stall knobs, lazy client reuse across bucket/billing-project contexts, DirectPath verification reliability, fallback behavior controlled by `GrpcPathStrategy`, and skipping control clients for localhost endpoints. Misclassification in storage layout affects rapid/zonal behavior, retry wrapping, and transport selection.

## Test Signals
This file is not directly tested in the assigned set, but `fake_storage_util.go` constructs `storageClient` instances for tests, `bucket_test.go` validates bucket type predicates consumed here, and control-client mocks support tests of layout/folder behavior elsewhere. Runtime logs around `GetStorageLayout`, DirectPath verification, fallback, and retry setup are important observability signals.
