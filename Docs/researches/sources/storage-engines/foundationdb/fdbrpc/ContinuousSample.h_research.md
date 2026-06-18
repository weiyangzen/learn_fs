# sources/storage-engines/foundationdb/fdbrpc/ContinuousSample.h

## Purpose
`ContinuousSample.h` provides a small template reservoir sampler that tracks a bounded random sample from a stream plus aggregate min, max, sum, population size, mean over the sample, median, and percentile queries.

## Important APIs, Types, and Functions
The template class `ContinuousSample<T>` exposes `addSample`, `getSamples`, `sum`, `mean`, `median`, `percentile`, `min`, `max`, `clear`, `getPopulationSize`, and `swap`. Private state includes `sampleSize`, `populationSize`, `sorted`, `samples`, `_min`, `_max`, and `_sum`.

## Control Flow
`addSample` updates aggregates, increments population, appends samples until capacity, then uses reservoir sampling probability `sampleSize / populationSize` to replace a random existing sample. Percentile queries sort the retained sample lazily and return the smallest element at least as large as the requested fraction.

## State and Persistence Behavior
All state is in memory. The sampler preserves aggregate population count and sum over all observed samples, but `mean()` is computed over retained samples rather than total `_sum / populationSize`. `clear` resets state but assigns zero to `_min`, `_max`, and `_sum`, which only works for numeric-like `T`.

## Dependencies and Integration Points
It depends on Flow platform/random headers, deterministic randomness, STL vector/algorithm, and math. It is a generic utility for metrics or diagnostics needing bounded samples.

## Risks and Edge Cases
`sampleSize == 0` would cause invalid replacement behavior after the first sample if not avoided by callers. `mean()` may surprise callers because it uses the sample reservoir, while `sum()` returns total accumulated sum. `clear` is not fully generic despite the template. Percentiles on an empty sample or invalid percentile return default `T()`.

## Test Signals
There are no direct tests in this subset. Indirect signals come from metrics or components using `ContinuousSample` and validating percentile/min/max behavior.
