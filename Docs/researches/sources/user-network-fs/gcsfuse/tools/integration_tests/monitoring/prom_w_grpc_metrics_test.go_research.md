<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/prom_w_grpc_metrics_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/prom_w_grpc_metrics_test.go

## Purpose

This suite verifies gRPC client metrics are exported when gcsfuse is mounted with gRPC protocol and experimental gRPC metrics enabled.

## Important APIs, Types, and Functions

`PromGrpcMetricsTest` embeds `PromTestBase`. `TestStorageClientGrpcMetrics` reads `hello.txt` and checks gRPC metric families with shared count/histogram assertion helpers. `TestPromGrpcMetricsSuite` skips when not running in a mounted-directory/GKE environment.

## Control Flow

The test reads the prepared file, then asserts `grpc_client_attempt_started` for the expected storage method: `BidiReadObject` for zonal buckets and `ReadObject` otherwise. It also asserts generic attempt started plus attempt duration, call duration, received compressed message size, and sent compressed message size histograms.

## State and Persistence Behavior

State is Prometheus metric state in the mounted gcsfuse process and the GCS object read. No test-specific persistence beyond the prepared file is introduced.

## Dependencies and Integration Points

It depends on monitoring setup flags with `--client-protocol=grpc --experimental-enable-grpc-metrics=true`, gRPC storage client instrumentation, and mounted-directory mode. Default suite skips on GCE VM static runs.

## Risks and Test Signals

Metric names are from gRPC instrumentation and can change. The environment skip means local/static test runs do not validate this path. Passing signal is non-zero gRPC attempt and histogram metrics after a read.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/prom_w_grpc_metrics_test.go -->
