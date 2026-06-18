# sources/object-store/apache-ozone/hadoop-hdds/common/src/test/java/org/apache/hadoop/hdds/tracing/TestLoopSampler.java

## Purpose
Tests `LoopSampler`, a deterministic ratio-based sampling helper used by tracing samplers.

## Important APIs, types, and functions
- Exercises constructor validation and `shouldSample` behavior for negative, zero, one, above-one, and half sampling ratios.
- Test cases include `negativeRatioThrows`, `zeroNeverSamples`, `oneAlwaysSamples`, `aboveOneIsCappedToAlwaysSample`, and `halfSamplesStatistically`.

## Control flow
The tests instantiate samplers with representative ratios and call the sampling decision repeatedly, asserting deterministic always/never behavior or approximate statistical behavior for 0.5.

## State and persistence behavior
Sampler state is in-memory counters/randomness used to decide sampling. No persistence.

## Dependencies and integration points
`LoopSampler` underlies trace and span sampling configuration in HDDS tracing.

## Risks and test signals
Bad ratio handling can produce too many or too few spans. Tests signal bounds handling and practical midpoint sampling behavior.
