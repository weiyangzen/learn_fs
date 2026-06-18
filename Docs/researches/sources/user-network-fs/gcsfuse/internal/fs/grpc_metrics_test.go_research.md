<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/grpc_metrics_test.go -->
# sources/user-network-fs/gcsfuse/internal/fs/grpc_metrics_test.go

## Purpose

This Go test file validates gRPC client metrics emitted when gcsfuse uses the gRPC storage client protocol. It uses a local reflective fake Google Storage service so tests can trigger client-side gRPC instrumentation without importing conflicting generated storage protobuf packages.

## Important APIs, Types, and Functions

`reflectFakeServer` implements dynamic handlers for `GetObject`, `ListObjects`, `ReadObject`, `StartResumableWrite`, and `WriteObject` using `dynamicpb` and `protoregistry`. `registerFakeStorageServer` manually registers the `google.storage.v2.Storage` service, including unary and streaming descriptors. `fakeStorageControlServer` returns a storage layout with HNS disabled. `createTestFileSystemWithGrpcMetrics` starts the fake gRPC service, a fake metadata server for project ID discovery, configures `storage.NewStorageHandle` with `ClientProtocol: cfg.GRPC` and `EnableGrpcMetrics`, then builds `fs.NewFileSystem`.

The tests are `TestGrpcMetrics_LookUpInode`, `TestGrpcMetrics_ReadFile`, and `TestGrpcMetrics_CreateFile`.

## Control Flow

Setup installs environment variables to bypass protobuf registration conflicts and point metadata lookup to the fake metadata server. The filesystem is wrapped with monitoring. Tests perform a short-timeout "poke" to avoid local DirectPath checks blocking the main operation, then execute lookup, read, or create/sync flows. Metrics are collected from an OpenTelemetry manual reader and asserted using subset/at-least matching for `grpc.client.attempt.started` and `grpc.client.call.duration`.

## State and Persistence Behavior

The gRPC server, metadata HTTP server, OpenTelemetry provider, and environment variables are process-global or local runtime resources cleaned with `t.Cleanup`. The fake service returns synthetic object metadata and read bytes; no durable storage is written. Timing sleeps account for delayed metric export.

## Dependencies and Integration Points

The file integrates `internal/storage`, `storageutil`, `gcsx.BucketManager`, `fs.ServerConfig`, monitoring wrappers, OpenTelemetry metrics, gRPC server APIs, storage control protobufs, and dynamic protobuf reflection. It tests the interaction between the gcsfuse FUSE layer, storage gRPC client, Google API gRPC metrics, and monitoring wrapper.

## Risks and Edge Cases

The tests are sensitive to DirectPath initialization behavior, environment variables, metric naming, and generated protobuf descriptors being registered in the global registry. The fake server implements only the paths needed by these tests; production behavior such as pagination, errors, checksums, and full streaming write semantics are not covered.

## Test Signals

Lookup verifies `GetObject` gRPC metrics. Read verifies `ReadObject` metrics. Create/sync verifies an attempted `BidiWriteObject` call even though the fake server returns unimplemented. Assertions use at-least/subset checks to tolerate extra client attempts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/fs/grpc_metrics_test.go -->
