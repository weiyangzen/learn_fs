# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/SpanSampler.java

## Purpose
OpenTelemetry sampler that combines root trace sampling with per-span sampling overrides for child spans.

## Important APIs and types
Constructor accepts a root `Sampler` and map of span names to `LoopSampler`. `shouldSample` delegates root spans to the root sampler, drops children of unsampled parents, applies a matching per-span sampler when present, and otherwise records sampled children. `getDescription` lists configured span names.

## Control flow and state
The sampler is immutable but uses the provided map reference. Parent sampling controls child eligibility before per-span sampling is considered, preventing orphaned sampled spans.

## Dependencies and integration points
Built by `TracingUtil.initialize` when `TracingConfig` supplies per-span sampling config. It uses OpenTelemetry SDK sampling APIs.

## Risks and test signals
Tests should cover root-span delegation, unsampled parent drop, sampled parent with explicit span rate zero/one, default child sampling, and description content. Span-name matching is exact.
