# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/hdds/tracing/LoopSampler.java

## Purpose
Independent probability sampler for named spans.

## Important APIs and types
Constructor accepts a ratio, rejects negative values, and caps values above one. `shouldSample()` returns false for zero, true for one, and otherwise compares a `ThreadLocalRandom` double to the probability.

## Control flow and state
Instances are immutable after construction.

## Dependencies and integration points
Used by `SpanSampler` for per-span sampling overrides parsed from tracing config.

## Risks and test signals
Tests should cover negative rejection, zero, one, values above one, and probabilistic behavior with enough sampling tolerance.
