<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/buffered_read_prom_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/buffered_read_prom_test.go

## Purpose

This skipped-by-default suite is intended to verify Prometheus metrics for buffered read behavior, including buffered read byte/latency metrics and fallback reasons for random-read detection and insufficient memory.

## Important APIs, Types, and Functions

`PromBufferedReadTest` embeds `PromTestBase`. Tests use `operations.ReadFile`, `operations.CreateFileOfSize`, `operations.OpenFileAsReadonly`, `io.ReadAll`, and the shared metric assertions `assertNonZeroCountMetric` and `assertNonZeroHistogramMetric`.

## Control Flow

`TestBufferedReadMetrics` reads `hello.txt` and expects GCS read/download byte counters and `buffered_read/read_latency`. `TestRandomReadFallback` creates a 16 MiB file and performs three decreasing-offset `ReadAt` calls so the third exceeds `--read-random-seek-threshold=2`, then expects `buffered_read_fallback_trigger_count{reason=random_read_detected}`. `TestInsufficientMemoryFallback` creates a 40 MiB file, opens two handles, reads all from the first to exhaust global blocks, then reads from the second and expects fallback reason `insufficient_memory`. `TestPromBufferedReadSuite` currently calls `t.SkipNow()` before running flag sets.

## State and Persistence Behavior

The tests create large files under the mounted test directory and inspect in-process Prometheus counters/histograms exposed by the mounted gcsfuse process. Buffered reader memory pool state is part of the behavior under test.

## Dependencies and Integration Points

It depends on monitoring setup flags enabling buffered read with specific block and memory limits, shared Prometheus parser/assertions, and static mounting.

## Risks and Test Signals

Because the suite is unconditionally skipped, it does not currently provide CI signal. If enabled, memory/fallback behavior may be sensitive to read scheduling and block accounting. Expected signal is non-zero buffered read and fallback metrics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/monitoring/buffered_read_prom_test.go -->
