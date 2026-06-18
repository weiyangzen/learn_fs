# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestSpanSampling.java

## Purpose
Tests span-specific OpenTelemetry sampling configuration and behavior.

## Important APIs, types, and functions
- Uses OpenTelemetry `Sampler`, `SamplingResult`, `SamplingDecision`, `SpanContext`, `TraceFlags`, `TraceState`, `SpanKind`, `Attributes`, and `Context`.
- Exercises parsing of span sampling config maps, invalid/malformed entries, rate clamping, child-span sampling decisions, and sampler descriptions.
- Uses configured span names and parent contexts to distinguish root trace decisions from child span decisions.

## Control flow
Parsing tests convert configuration strings to name-to-rate maps. Sampling tests create sampled and unsampled parent contexts, invoke the sampler with span names, and assert record/drop decisions according to trace-level and span-level sampling rules.

## State and persistence behavior
State consists of in-memory maps of span names to sampler ratios and OpenTelemetry context objects. No persistence.

## Dependencies and integration points
This file covers HDDS tracing integration with OpenTelemetry SDK sampling APIs.

## Risks and test signals
Incorrect parsing or parent handling can flood tracing backends or lose important child spans. The suite signals malformed-config tolerance, rate caps, parent unsampled behavior, and configured span overrides.
