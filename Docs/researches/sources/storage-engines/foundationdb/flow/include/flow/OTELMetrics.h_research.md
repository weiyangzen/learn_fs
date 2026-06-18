<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/OTELMetrics.h -->
# sources/storage-engines/foundationdb/flow/include/flow/OTELMetrics.h

Purpose: This header defines a compact in-process representation of OpenTelemetry metric payloads and msgpack serializers used by FoundationDB's metric export path. It models number data points, sums, gauges, and DDSketch-like histograms without depending on generated OTEL protobuf classes.

Important APIs and types: The main namespace is `OTEL`. Types include `Attribute`, `AggregationTemporality`, `DataPointFlags`, `NumberDataPoint`, `OTELSum`, `OTELGauge`, `HistogramDataPoint`, and `OTELHistogram`. Inline `serialize` overloads write each type into `MsgpackBuffer` using helper functions from `Msgpack.h`. `OTELSum::getMsgpackBytes` estimates encoded size.

Control flow: Constructors stamp datapoints with `now()` and initialize flags to `FLAG_NONE`. Number data points hold either `int64_t` or `double` in `std::variant`, and serialization branches on the active alternative. Histograms serialize the error guarantee, attributes, timestamps, count, sum, min, max, bucket vector, and flags. Sums default to cumulative monotonic aggregation; histograms default to delta aggregation.

State and persistence behavior: The classes are plain payload holders; persistence occurs through msgpack buffers consumed by the metrics pipeline. `HistogramDataPoint::buckets` is `const`, making bucket contents immutable after construction, while `count` is initialized to `buckets.size()` rather than the sum of bucket counts. Start times default to `-1` in some datapoints, which encodes an unset sentinel.

Dependencies and integration points: The file depends on `flow/flow.h`, `Msgpack.h`, `std::variant`, and vectors. It is referenced by `TDMetric.h` and the OTLP export helpers such as `createOtelGauge`. It bridges FoundationDB metric handles and external OTEL receivers.

Risks: The histogram format intentionally diverges from OTEL protobuf by using DDSketch buckets and 32-bit bucket values, so receivers must understand this contract and sign-extend or widen counts. `NumberDataPoint::MsgpackBytes` is an approximation, especially for attributes. `HistogramDataPoint::startTime` is not explicitly initialized by its constructor, unlike `NumberDataPoint`.

Test signals: Tests should validate msgpack field ordering and type tags for int, double, attributes, sums, gauges, and histograms; confirm byte-size estimates remain conservative enough for batching; and verify receivers correctly interpret 32-bit histogram buckets, temporality, unset start time, and flags.
<!-- END_FILE_RESEARCH: sources/storage-engines/foundationdb/flow/include/flow/OTELMetrics.h -->
