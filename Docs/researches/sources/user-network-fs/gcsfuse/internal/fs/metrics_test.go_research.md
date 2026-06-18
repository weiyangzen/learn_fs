# sources/user-network-fs/gcsfuse/internal/fs/metrics_test.go

Purpose: validates OpenTelemetry-backed metrics emitted by monitored filesystem operations, read paths, file cache behavior, GCS request accounting, read block-size histograms, and streaming-write fallback reasons.

Important APIs/types: `serverConfigParams` controls read/write/cache/streaming options for test filesystem creation. `createTestFileSystemWithMetrics` installs a manual OTel metric reader, creates `metrics.NewOTelMetrics`, builds a fake bucket and `fs.ServerConfig`, optionally configures file cache or sparse chunk cache, and returns the bucket, filesystem, metric handle, and reader. Tests wrap the server with `wrappers.WithMonitoring`.

Control flow and state: operation metrics tests create minimal FUSE ops (`LookUpInodeOp`, `OpenFileOp`, `ReadFileOp`, `MkDirOp`, etc.), call server methods directly, wait briefly for processing, and verify `fs/ops_count` and `fs/ops_latency` with `fs_op` attributes. Unsupported operations such as xattrs, fallocate, and hard links still emit metrics under either their explicit op or `Others`.

Read/cache metrics: buffered read tests expect `gcs/download_bytes_count`, `gcs/read_bytes_count`, and buffered latency. Sequential and random file-cache tests assert cache-hit labels, read types, and byte counts, including range-read disabled behavior. Sparse cache tests verify only the relevant chunk is downloaded. Kernel multi-range reader and GCS reader tests distinguish parallel, sequential, and random read types and request method metrics.

Persistence/instrumentation state: tests use fake bucket content and direct FUSE ops rather than mounting. File cache uses a temporary cache directory. Streaming-write fallback tests check fallback counters for existing files, out-of-order writes, and concurrency-limit breach.

Dependencies and integration: integrates `internal/fs`, monitoring wrappers, fake storage, `cfg`, `metrics` verification helpers, OTel SDK manual reader, `fuseops`, and tracing noop.

Risks: metric assertions are coupled to exact metric names and attribute sets. `waitForMetricsProcessing` is sleep-based. Global OTel meter provider is temporarily replaced, so cleanup is important and present. Direct server calls bypass kernel behavior.

Test signals: strong coverage for observability regressions across filesystem ops, read implementations, cache modes, GCS reads, block-size histograms, and streaming write fallback accounting.
