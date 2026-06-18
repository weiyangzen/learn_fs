<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/setup_test.go

## Purpose

This package setup file provides the shared Prometheus monitoring test harness. It configures default monitoring flag sets, mounts gcsfuse with log/cache path rewriting, prepares per-test files, fetches `/metrics`, and provides metric assertion helpers.

## Important APIs, Types, and Functions

It defines `env`, `testEnv`, `mountFunc`, and `PromTestBase`. Shared helpers include `mountGCSFuseAndSetupTestDir`, `parsePortFromFlags`, `parsePromFormat`, `assertNonZeroCountMetric`, and `assertNonZeroHistogramMetric`. `TestMain` configures seven default monitoring entries.

## Control Flow

`PromTestBase.SetupSuite` sets per-suite log path and mounts. `SetupTest` sanitizes the test name, creates a GCS directory, and writes `hello.txt`. Metric parsing performs HTTP GET against `localhost:<port>/metrics` and parses Prometheus text format. Assertions scan metric families for matching type, label, and non-zero values. `TestMain` builds defaults for OTel/file cache, buffered read, gRPC metrics, and kernel reader with distinct ports, initializes storage, delegates mounted-directory runs, otherwise sets up test bucket, rewrites temp paths, runs static mounting tests, cleans the monitoring prefix, and exits.

## State and Persistence Behavior

It owns the mounted gcsfuse process exposing Prometheus state, test GCS objects under `monitoring`, log/cache directories, and shared storage client/context. Metrics are cumulative across suite lifetime.

## Dependencies and Integration Points

It depends on Cloud Storage clients, static mounting, setup/test-suite config, Prometheus `expfmt`, client model types, and Testify suite/require. All monitoring test files use this harness.

## Risks and Test Signals

Port collisions, stale metrics, and cumulative counters can affect assertions. Path override is required for GCE. Success is mount startup with metrics endpoint reachable and expected metric families non-zero after filesystem actions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/setup_test.go -->
