<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/prom_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/prom_test.go

## Purpose

This suite validates general gcsfuse Prometheus/OTel metrics for stat, list, xattr error, read, file-cache, GCS request, and reader counters.

## Important APIs, Types, and Functions

`PromTest` embeds `PromTestBase`. Tests call `os.Stat`, `os.ReadDir`, `xattr.Set`, `os.ReadFile`, and shared `assertNonZeroCountMetric`/`assertNonZeroHistogramMetric`.

## Control Flow

`TestStatMetrics` stats `hello.txt` and expects `LookUpInode`, `StatObject`, and latency metrics. `TestFsOpsErrorMetrics` stats a missing file and expects filesystem error and latency metrics. `TestListMetrics` lists the test directory and expects `ReadDir`, `OpenDir`, and `ListObjects` metrics. `TestSetXAttrMetrics` attempts unsupported xattr set and expects an `Others` fs error. `TestReadMetrics` reads `hello.txt` and expects file-cache sequential read, cache miss, open/read fs ops, NewReader request, reader open/close, download bytes, and latency metrics. The suite runner iterates flag sets and parses ports.

## State and Persistence Behavior

Metrics are cumulative process state exposed on `/metrics`. Each test starts with a prepared `hello.txt`, but counters may include prior tests; assertions only require non-zero matching samples.

## Dependencies and Integration Points

It depends on monitoring setup, Prometheus text parser, xattr package, and static mounting with file cache enabled. It exercises both flat and HNS/zonal port variants through config.

## Risks and Test Signals

Metric names/labels are tightly coupled to instrumentation. Counters being cumulative can mask per-test missing increments if earlier tests set the same labels. Passing signal is presence of non-zero expected metric families and labels after operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/prom_test.go -->
