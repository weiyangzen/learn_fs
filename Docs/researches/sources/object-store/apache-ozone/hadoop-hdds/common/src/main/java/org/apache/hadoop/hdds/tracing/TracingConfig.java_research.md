# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/TracingConfig.java

## Purpose
Reconfigurable OpenTelemetry tracing configuration object for Ozone services.

## Important APIs and types
Config fields define enablement, OTLP endpoint, root trace sampler ratio, and per-span sampling string under the `ozone.tracing` group. `validate()` applies environment fallbacks and defaults. Getters expose final values.

## Control flow and state
`validate` fills an empty endpoint from `OTEL_EXPORTER_OTLP_ENDPOINT`, defaulting to `http://localhost:4317`. If sampler ratio is negative, it tries `OTEL_TRACES_SAMPLER_ARG`; invalid or out-of-range values become `1.0`. Empty span sampling can be filled from `OTEL_SPAN_SAMPLING_ARG`.

## Dependencies and integration points
Consumed by `TracingUtil.initTracing` and `isTracingEnabled`. It uses HDDS config annotations and `ReconfigurableConfig` to support runtime updates.

## Risks and test signals
Tests should cover config value priority, environment fallback, invalid env parsing, out-of-range sampler clamping, blank endpoint defaulting, and reconfigurable metadata. Defaulting invalid sampler ratios to `1.0` can unexpectedly increase tracing volume.
