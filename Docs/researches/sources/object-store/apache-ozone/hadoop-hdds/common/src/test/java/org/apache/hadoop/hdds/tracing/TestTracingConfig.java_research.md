# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestTracingConfig.java

## Purpose
Tests typed tracing configuration parsing for trace sampling ratio, tracing endpoint, and explicit span sampling rules.

## Important APIs, types, and functions
- Uses `InMemoryConfigurationForTesting`, `MutableConfigurationSource`, and `TracingConfig`.
- Covers clamping ratios above one, valid ratios, negative ratio handling, explicit endpoint, and span sampling config string parsing.

## Control flow
Tests set tracing configuration keys in memory, bind to `TracingConfig`, and assert normalized values returned by getters.

## State and persistence behavior
Configuration is in-memory only. It models persisted Ozone config keys without disk IO.

## Dependencies and integration points
`TracingConfig` feeds `TracingUtil.initTracing` and OpenTelemetry exporter/sampler setup.

## Risks and test signals
Bad config normalization can over-sample, under-sample, or target the wrong collector endpoint. The tests signal bounds and explicit override behavior.
