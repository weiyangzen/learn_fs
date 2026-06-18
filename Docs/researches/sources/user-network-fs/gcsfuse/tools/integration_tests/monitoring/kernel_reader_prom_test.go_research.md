<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/kernel_reader_prom_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/kernel_reader_prom_test.go

## Purpose

This suite verifies Prometheus metrics emitted by the kernel reader / multi-range downloader path for zonal buckets.

## Important APIs, Types, and Functions

`PromKernelReaderTest` embeds `PromTestBase`. `TestKernelReaderMetrics` uses `client.SetupFileInTestDirectory`, `os.ReadFile`, and shared Prometheus metric assertion helpers.

## Control Flow

The test creates a 10 MiB file in a per-test GCS directory, reads it through the mount, then asserts non-zero filesystem read count, parallel GCS download/read byte and read counters, and GCS request count/latency for `MultiRangeDownloader::Add`. `TestPromKernelReaderSuite` builds matching flag sets, parses the Prometheus port from flags, and runs the suite.

## State and Persistence Behavior

State includes a large GCS object and Prometheus counters/histograms exposed by the mounted gcsfuse process. Each test uses a sanitized per-test directory name.

## Dependencies and Integration Points

It depends on monitoring setup config entry `--prometheus-port=9193` for zonal buckets and default kernel reader behavior. It uses shared setup/client and metric parsing utilities.

## Risks and Test Signals

The suite is compatible only with zonal bucket runs in default config. If file size or reader thresholds change, the read may not use the parallel path. Passing signal is non-zero parallel read and MultiRangeDownloader metrics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/kernel_reader_prom_test.go -->
