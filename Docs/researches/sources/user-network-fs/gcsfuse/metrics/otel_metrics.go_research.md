# Research: sources/user-network-fs/gcsfuse/metrics/otel_metrics.go

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-009590`: lines 1-2598, `Docs/researches/chunks/subset-b-009590_research.md`
- `subset-b-009591`: lines 2599-4417, `Docs/researches/chunks/subset-b-009591_research.md`

## Chunk Research

### subset-b-009590: lines 1-2598

# sources/user-network-fs/gcsfuse/metrics/otel_metrics.go lines 1-2598

## Scope

This chunk covers the first 2,598 lines of the generated OpenTelemetry metrics implementation for gcsfuse. The source file is explicitly marked `DO NOT EDIT - FILE IS AUTO-GENERATED`. This range includes imports, precomputed attribute sets, the `histogramRecord` and `otelMetrics` types, most concrete `MetricHandle` recording methods, and the beginning of `MetadataCacheReadCount`. It stops mid-function at the `cacheHit == false` / `EntryStatusNegativeAttr` branch, so constructor setup, callback registration details after line 2,598, helpers, `Close`, and the rest of metadata-cache handling are owned by later chunks.

## Purpose

`otel_metrics.go` is the concrete metrics backend behind `metrics.MetricHandle`. It maps typed metric method calls such as `FsOpsCount`, `GcsRequestCount`, and `FileCacheReadCount` into OpenTelemetry counters and histograms while keeping attribute cardinality fixed to generated enum combinations.

The design in this chunk has two main jobs:

- convert public metric method parameters into predeclared OpenTelemetry attribute sets and per-attribute atomic counters;
- keep hot-path metric recording low overhead by using `atomic.Int64` counters for observable counters and a bounded asynchronous channel for histograms.

## Important Types And Data

The file imports `context`, `errors`, `sync`, `sync/atomic`, `time`, gcsfuse's internal `logger`, and OpenTelemetry packages `otel`, `attribute`, and `metric`.

Key declarations in this chunk:

- `const logInterval = 5 * time.Minute`: cadence for sampled logging of unrecognized attributes, with helper functions outside this range.
- `unrecognizedAttr atomic.Value`: process-global storage for one sampled unknown attribute value.
- many `metric.WithAttributeSet(attribute.NewSet(...))` variables: static attribute options for every supported attribute combination, such as `fs_op=ReadFile`, `gcs_method=NewReader`, `cache_hit=true`, or `read_type=Sequential`.
- `histogramRecord`: carries `ctx`, `metric.Int64Histogram`, numeric value, and optional `metric.RecordOption` for deferred histogram recording.
- `otelMetrics`: concrete implementation state. In this range it contains `ch chan histogramRecord`, a `WaitGroup`, hundreds of pointers to `atomic.Int64` counters, and histogram instruments for buffered-read latency, file-cache latency, filesystem operation latency, GCS request latency, and read block sizes.

The generated field layout mirrors attribute combinations. For example, `fs/ops_error_count` expands into a field for each `FsErrorCategory` and `FsOp` pair, while `metadata_cache/read_count` expands into fields for `cache_hit`, `entry_status`, and `lookup_detail`.

## APIs And Functions

This chunk implements the following `otelMetrics` methods:

- `BufferedReadFallbackTriggerCount(inc, reason)`: increments counts for buffered reader fallback reasons `insufficient_memory` or `random_read_detected`.
- `BufferedReadReadLatency(ctx, latency)`: records buffered-reader read latency in microseconds through the histogram queue.
- `FileCacheReadBytesCount(inc, readType)`: increments file-cache byte counters for `Parallel`, `Random`, `Sequential`, or `Unknown` read types.
- `FileCacheReadCount(inc, cacheHit, readType)`: tracks read request counts split by cache hit boolean and read type.
- `FileCacheReadLatencies(ctx, latency, cacheHit)`: records microsecond file-cache latency with a `cache_hit` attribute.
- `FsOpsCount(inc, fsOp)`: increments total filesystem operation counts for the generated `FsOp` enum values.
- `FsOpsErrorCount(inc, fsErrorCategory, fsOp)`: increments the filesystem error counter for a cross-product of 16 error categories and 25 filesystem operations.
- `FsOpsLatency(ctx, latency, fsOp)`: records filesystem operation latency in microseconds, attributed by operation.
- `FsStreamingWriteFallbackCount(inc, openMode, writeFallbackReason)`: counts streaming-write fallback reasons across five open modes and four fallback reasons.
- `GcsDownloadBytesCount(inc, readType)`: counts downloaded bytes for buffered, parallel, random, and sequential read types.
- `GcsReadBytesCount(inc)`: counts raw GCS read bytes with no attributes.
- `GcsReadCount(inc, readType)`: counts GCS reads for parallel, random, sequential, and unknown read types.
- `GcsReaderCount(inc, ioMethod)`: counts GCS readers opened or closed.
- `GcsRequestCount(inc, gcsMethod)`: counts calls to generated GCS method names including object, folder, appendable-writer, chunk-writer, and multi-range downloader operations.
- `GcsRequestLatencies(ctx, latency, gcsMethod)`: records GCS request latency in milliseconds, attributed by method.
- `GcsRetryCount(inc, retryErrorCategory)`: counts retry categories `OTHER_ERRORS` and `STALLED_READ_REQUEST`.
- start of `MetadataCacheReadCount(inc, cacheHit, entryStatus, lookupDetail)`: validates nonnegative increments and handles the `cacheHit == true` branch plus the start of `cacheHit == false`.

All counter methods in this range reject negative increments by logging an error and returning without mutation. Histogram methods do not check for negative durations in this chunk.

## Control Flow

Counter methods follow a consistent generated pattern:

1. Check `inc < 0`; if true, call `logger.Errorf` with the metric name and return.
2. Switch over each typed attribute argument in a nested order matching the metric schema.
3. On a recognized attribute combination, call `.Add(inc)` on the matching `atomic.Int64`.
4. On an unrecognized enum value, call `updateUnrecognizedAttribute(string(value))` and return without updating a counter.

Histogram methods in this range follow a different pattern:

1. Convert `time.Duration` to the configured integer unit: microseconds for buffered reads, file-cache reads, and filesystem operations; milliseconds for GCS request latencies.
2. Build a `histogramRecord` with the proper histogram instrument and static attribute set.
3. Try to send it to `o.ch` using a nonblocking `select`.
4. Drop the record silently if the channel is full.

`FsOpsErrorCount` is the most expansive visible method. It switches first on `FsErrorCategory` values such as `DEVICE_ERROR`, `DIR_NOT_EMPTY`, `FILE_DIR_ERROR`, `FILE_EXISTS`, `INTERRUPT_ERROR`, `INVALID_ARGUMENT`, `INVALID_OPERATION`, `IO_ERROR`, `MISC_ERROR`, `NETWORK_ERROR`, `NOT_A_DIR`, `NOT_IMPLEMENTED`, `NO_FILE_OR_DIR`, `PERM_ERROR`, `PROCESS_RESOURCE_MGMT_ERROR`, and `TOO_MANY_OPEN_FILES`; each category then switches across the same generated filesystem operation set.

The chunk ends inside `MetadataCacheReadCount`: the visible complete `cacheHit == true` branch handles empty, `negative`, and `positive` `entry_status` values, each split by `found`, `not_found`, and `ttl_expired`. The `cacheHit == false` branch is only partially visible.

## State And Persistence Behavior

The persistent runtime state in this chunk is in-memory only:

- atomic counters accumulate until the `otelMetrics` instance is closed or discarded;
- histograms are buffered in `o.ch` and later recorded by worker goroutines created outside this chunk;
- `unrecognizedAttr` is a global sampled value for unknown attributes and is not persisted beyond process memory.

Observable counters are not updated directly through OpenTelemetry instruments at call time. Instead, these methods mutate atomics; OpenTelemetry callbacks registered in `NewOTelMetrics` later observe nonzero values. The helper `conditionallyObserve` appears after this chunk and explains the nonzero-only observation behavior.

Histogram persistence is intentionally lossy under pressure. If the histogram channel is full, the nonblocking send falls through the `default` branch and the sample is dropped to keep application operations from blocking on metrics.

## Dependencies And Integration Points

Primary local integration points:

- `sources/user-network-fs/gcsfuse/metrics/metric_handle.go`: defines the `MetricHandle` interface and all typed attribute enums consumed by this implementation.
- `sources/user-network-fs/gcsfuse/metrics/noop_metrics.go`: provides the no-op implementation with the same method surface.
- `sources/user-network-fs/gcsfuse/cmd/legacy_main.go`: constructs this backend with `metrics.NewOTelMetrics(ctx, workers, bufferSize)` when metrics are enabled.
- filesystem monitoring wrappers under `internal/fs/wrappers/monitoring.go`: call filesystem operation count, latency, and error methods.
- GCS monitoring under `internal/monitor/bucket.go`: records GCS request latency.
- buffered read and cache readers under `internal/bufferedread` and `internal/gcsx`: record fallback, read count, and cache metrics.

External dependencies are OpenTelemetry's global meter provider and metric API, plus `sync/atomic` for low-contention counters. This generated code assumes the string constants in `metric_handle.go` remain aligned with the generated attribute sets here.

## Risks And Maintenance Notes

The file is generated and highly repetitive. Manual edits are risky because each metric requires coordinated changes across attribute-set declarations, `otelMetrics` fields, constructor initialization/callbacks, record methods, tests, and the public interface.

Important behavioral risks in this chunk:

- unknown attributes are not counted and only one sampled value is retained for logging, so a caller using stale enum strings can lose metric data quietly apart from sampled logs;
- histogram recording is best-effort and can drop samples when `bufferSize` or worker throughput is insufficient;
- counter methods prevent negative increments, but up/down counter methods outside this range intentionally differ;
- durations are converted to integer microseconds or milliseconds, so sub-unit precision is truncated;
- `EntryStatusAttr` is the empty string, which produces attribute sets without `entry_status` in generated metadata-cache counters; this is intentional but easy to misread in tests and dashboards;
- the cross-product expansion for `FsOpsErrorCount` creates a large maintenance surface whenever error categories or filesystem operations change.

Because this chunk stops mid-`MetadataCacheReadCount`, whole-function conclusions need reconciliation with the next chunk.

## Test Signals

`sources/user-network-fs/gcsfuse/metrics/otel_metrics_test.go` provides direct test coverage for this generated implementation using a manual OpenTelemetry reader. The tests create an `otelMetrics` through `NewOTelMetrics`, call methods with specific attribute combinations, collect metrics, and compare encoded attribute/value maps.

Visible test signals relevant to this chunk include:

- table-driven coverage for supported attribute values on `BufferedReadFallbackTriggerCount`, file-cache counters, filesystem operation/error counters, GCS request counters/latencies, retry counters, and metadata-cache read counts;
- negative-increment cases asserting that counters are not decremented or updated by invalid negative values;
- histogram tests that wait briefly for asynchronous processing before collecting manual-reader data;
- metadata-cache tests covering both cache-hit values, empty/negative/positive entry status, and found/not-found/ttl-expired lookup detail combinations.

Integration tests under `internal/fs` and GCS-related packages instantiate `NewOTelMetrics` and exercise the metrics backend through real wrappers, giving additional signal that the generated implementation satisfies the `MetricHandle` contract.

### subset-b-009591: lines 2599-4417

# sources/user-network-fs/gcsfuse/metrics/otel_metrics.go lines 2599-4417

## Purpose

This chunk is the tail of the generated OpenTelemetry metrics implementation for `gcsfuse`. It finishes the `MetadataCacheReadCount` attribute dispatch, defines the last metric update methods, builds a complete `otelMetrics` instance in `NewOTelMetrics`, and provides shutdown plus observation/logging helpers.

The core purpose is to translate typed metric API calls into low-cardinality OpenTelemetry instruments. Counter-like metrics are stored in per-attribute `atomic.Int64` cells and exported through asynchronous observable callbacks, while histogram values are pushed through a bounded channel to worker goroutines that call OpenTelemetry `Record`.

## High-Level Structure

- Lines 2599-2626: Completes the nested metadata-cache counter switch for `cache_hit=false`, including `EntryStatusNegativeAttr` and `EntryStatusPositiveAttr` by `LookupDetail` value. Unknown enum values are not recorded; they update the sampled unrecognized-attribute state.
- Lines 2628-2636: Implements `ReadBlockSizes`, a histogram recorder for `read/block_sizes`. It enqueues a `histogramRecord` on `o.ch` and silently drops the record if the channel is full.
- Lines 2638-2654: Implements test-only up-down counter methods: one without attributes and one keyed by `RequestTypeAttr1Attr` or `RequestTypeAttr2Attr`.
- Lines 2656-2673: Starts `NewOTelMetrics` by creating the bounded histogram channel, launching sampled logging, starting `workers` goroutines to drain histogram records, and acquiring the `gcsfuse` OpenTelemetry meter.
- Lines 2674-3199: Declares local `atomic.Int64` backing cells for every observable metric/attribute combination used by this constructor: buffered read fallback reasons, file cache read bytes/counts, filesystem op counts, filesystem error category/op matrix, streaming write fallback open mode/reason matrix, GCS read/request/retry metrics, metadata cache combinations, and test up-down counters.
- Lines 3201-3841: Registers 20 OpenTelemetry instruments (`err0` through `err19`): observable counters, histograms, and observable up-down counters. Callback bodies call `conditionallyObserve` for cumulative counters and `observeUpDownCounter` for up-down values.
- Lines 3843-3846: Joins instrument registration errors with `errors.Join`; any registration failure aborts construction.
- Lines 3848-4368: Returns an `otelMetrics` struct wiring the channel, wait group, histogram instruments, and pointers to every local atomic counter. The local atomics escape to heap because the returned struct and OpenTelemetry callbacks hold their addresses.
- Lines 4371-4374: `Close` closes the histogram channel and waits for histogram worker goroutines to finish draining records already accepted into the channel.
- Lines 4376-4417: Helper functions observe nonzero counters, always observe up-down counters, store the first unrecognized attribute value, start periodic sampled logging, and emit a trace log for unknown metric attributes.

## Important APIs And Functions

- `NewOTelMetrics(ctx context.Context, workers int, bufferSize int) (*otelMetrics, error)` is the constructor and integration point. It creates the async histogram worker pool, registers all instruments on `otel.Meter("gcsfuse")`, checks registration errors, and returns the concrete metrics implementation used by callers.
- `ReadBlockSizes(ctx context.Context, value int64)` records read block-size histogram samples. Unlike observable counters, histogram updates are asynchronous and lossy under channel pressure.
- `TestUpdownCounter(inc int64)` and `TestUpdownCounterWithAttrs(inc int64, requestType RequestType)` mutate observable up-down counter backing atomics. The attributed variant rejects unrecognized request types through `updateUnrecognizedAttribute`.
- `Close()` is the lifecycle terminator for histogram workers. After it closes `o.ch`, any later histogram method that sends to `o.ch` can panic, so callers must coordinate shutdown with metric use.
- `conditionallyObserve` exports an observable counter only when its atomic value is greater than zero. This suppresses zero-valued attribute series and limits exported cardinality.
- `observeUpDownCounter` always exports the current value, including zero and negative values, matching up-down counter semantics.
- `updateUnrecognizedAttribute`, `startSampledLogging`, and `logUnrecognizedAttribute` implement sampled diagnostics for enum values that are not in the generated attribute matrix.

## Registered Instruments

This chunk registers the following metric names and kinds:

- Observable counters: `buffered_read/fallback_trigger_count`, `file_cache/read_bytes_count`, `file_cache/read_count`, `fs/ops_count`, `fs/ops_error_count`, `fs/streaming_write_fallback_count`, `gcs/download_bytes_count`, `gcs/read_bytes_count`, `gcs/read_count`, `gcs/reader_count`, `gcs/request_count`, `gcs/retry_count`, and `metadata_cache/read_count`.
- Histograms: `buffered_read/read_latency`, `file_cache/read_latencies`, `fs/ops_latency`, `gcs/request_latencies`, and `read/block_sizes`.
- Observable up-down counters: `test/updown_counter` and `test/updown_counter_with_attrs`.

The latency histograms use explicit buckets. Buffered read, file cache, and filesystem latencies are in microseconds with wide boundaries from tens of microseconds through hundreds of seconds. GCS request latencies are in milliseconds. `read/block_sizes` is in bytes, with boundaries from 0 through 128 MiB.

## Control Flow

1. Metric update methods validate generated enum values with nested `switch` statements. A valid attribute combination adds `inc` to its dedicated atomic counter; an invalid attribute calls `updateUnrecognizedAttribute` and returns without recording.
2. Histogram methods create a `histogramRecord` containing context, instrument, value, and optional attributes, then attempt a nonblocking send to `o.ch`.
3. `NewOTelMetrics` starts a sampled logging goroutine before instrument registration. The logging goroutine exits only when the supplied `ctx` is canceled.
4. `NewOTelMetrics` starts `workers` goroutines that range over the histogram channel. Each worker records with attributes when `record.attributes != nil`; otherwise it records the bare value.
5. The constructor declares all observable counter backing state as local atomics, then registers OpenTelemetry callbacks that close over those local atomics.
6. Each observable counter callback loads every known attribute cell for that metric and calls `obsrv.Observe` only for cells whose value is positive. The up-down callbacks observe unconditionally.
7. The constructor joins all instrument creation errors. On success, it returns an `otelMetrics` whose fields point to the same atomics captured by callbacks; on failure, it returns `nil, err`.
8. `Close` closes the channel and waits for workers to leave their `range` loops after the channel is drained.
9. Sampled logging keeps a single global `unrecognizedAttr` value. The first unknown attribute since the last log tick wins via `CompareAndSwap("", newValue)`, and the ticker swaps it back to empty before logging.

## State And Persistence Behavior

- There is no on-disk persistence. All metric state lives in memory in `atomic.Int64` counters, OpenTelemetry instruments/callback registrations, the histogram channel, worker goroutines, and the global `unrecognizedAttr`.
- Counter state is cumulative for the lifetime of the `otelMetrics` instance. Observable counter callbacks report the current accumulated value rather than deltas; the OpenTelemetry SDK/exporter interprets temporality downstream.
- Histogram records are transient. A record is persisted only long enough to sit in the bounded channel; if the channel is full, the sample is dropped immediately.
- The constructor stores pointers to local atomics in the returned struct. This is intentional escape behavior and lets both update methods and registered callbacks share the same cells.
- `unrecognizedAttr` is package-global. Calling `NewOTelMetrics` resets it to the empty string and starts another sampled logging goroutine, so multiple metrics instances share and overwrite the same unknown-attribute diagnostic slot.
- `Close` drains accepted histogram records but does not unregister OpenTelemetry observable callbacks and does not stop sampled logging. Logging stops through the constructor context, not through `Close`.

## Dependencies And Integration Points

- Depends on `go.opentelemetry.io/otel` for the global meter provider and `go.opentelemetry.io/otel/metric` for instrument creation, callback registration, observation options, histograms, and observers.
- Depends on generated attribute sets defined earlier in the file, such as `fsOpsCountFsOpReadFileAttrSet`, GCS method attr sets, streaming write fallback attr sets, and metadata cache attr sets.
- Depends on enum-like attribute types and constants defined earlier in the generated file, including `RequestType`, `EntryStatus`, `LookupDetail`, read types, GCS methods, filesystem ops, filesystem error categories, open modes, and fallback reasons.
- Integrates with the rest of gcsfuse through the concrete `otelMetrics` methods called by filesystem, cache, GCS, and buffered-read code paths. Those callers do not construct OpenTelemetry options directly; they pass typed attributes to these generated methods.
- Integrates with `internal/logger` only for trace-level reporting of undeclared attributes.
- Uses Go concurrency primitives: `sync.WaitGroup`, `sync/atomic.Int64`, goroutines, and channels.

## Risks And Edge Cases

- Histogram recording is intentionally lossy. `ReadBlockSizes` and other histogram methods using the same channel drop samples when `bufferSize` is exhausted or workers cannot keep up, which can bias latency/size distributions under load.
- `Close` is not idempotent. Calling it twice closes an already closed channel and panics. Calling histogram update methods after `Close` can also panic on send to a closed channel.
- Constructor failure after workers have started can leak goroutines because the error path returns before closing `ch` or waiting on `wg`. Instrument registration errors are probably rare, but tests using a failing meter provider should check this.
- `startSampledLogging` is called before registration succeeds. If construction fails, the logging goroutine still runs until `ctx` is canceled.
- `workers <= 0` is accepted by the `for range workers` loop semantics. With zero workers, histogram sends can fill the buffer and then all future histogram samples are dropped; with a zero buffer and zero workers, all histogram samples are dropped.
- Observable counter callbacks suppress zero values by design. Dashboards or tests expecting an explicit zero time series for every generated attribute combination will not see one until the value becomes positive.
- Up-down counters always observe current values, including zero. This differs from counter observation and is intentional but worth noting for test expectations.
- Unknown attribute diagnostics are sampled and lossy. Only one undeclared value is retained between log ticks, shared globally across all metrics instances and all metric methods.
- The generated filesystem error-count matrix is large. Adding or removing filesystem ops or error categories must keep declarations, callbacks, struct fields, update switches, and returned field wiring synchronized; because this file is generated, changes should flow through the generator.

## Test Signals

- Constructor tests should verify `NewOTelMetrics` returns a non-nil instance with a normal OpenTelemetry meter provider and that `Close` drains worker goroutines without hanging.
- Observable counter tests should increment representative metrics and collect/export observations to confirm only positive counter cells are observed with the expected attribute sets.
- Metadata cache tests should cover valid `cache_hit`, `entry_status`, and `lookup_detail` combinations from the tail switch, plus an invalid value path that triggers sampled unknown-attribute logging rather than incrementing a counter.
- Histogram tests should exercise `ReadBlockSizes` with at least one worker and enough buffer to confirm samples reach the histogram, and with a saturated channel to confirm callers do not block.
- Lifecycle tests should avoid calling `Close` twice or recording histograms after `Close` unless intentionally asserting panic behavior.
- Error-path tests using a custom failing meter provider should check whether workers/logging goroutines remain live after `NewOTelMetrics` returns an error.
- Static regeneration tests should compare generated output against the source metric catalog, especially the 20 registered instruments, explicit bucket boundaries, and the large fs error category by fs op matrix.
