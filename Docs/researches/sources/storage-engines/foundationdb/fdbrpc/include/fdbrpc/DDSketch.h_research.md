# sources/storage-engines/foundationdb/fdbrpc/include/fdbrpc/DDSketch.h

## Purpose
`DDSketch.h` implements approximate quantile sketches for non-negative values, including fast floating-point, slow logarithmic, and fixed-accuracy unsigned integer variants.

## Important APIs, Types, and Functions
`fastLogger` provides `fastlog` and `reverseLog`. `DDSketchBase<Impl,T>` implements sample insertion, `mean`, `median`, `percentile`, `min`, `max`, `getSum`, `clear`, `getPopulationSize`, `getErrorGuarantee`, `getBucketSize`, `getSamples`, and `mergeWith`. Concrete implementations are `DDSketch<T>`, `DDSketchSlow<T>`, and `DDSketchFastUnsigned`.

## Control Flow
Adding a sample updates min/max/sum/population, counts near-zero samples separately, maps positive samples into a bucket through the implementation's `getIndex`, and increments that bucket. Percentile lookup computes a zero-based target rank, handles zero samples, then scans buckets upward for lower percentiles or downward for upper percentiles and converts the chosen bucket back to an estimated value. Merging asserts compatible error guarantees and bucket sizes, then adds bucket populations and summary fields.

## State and Persistence Behavior
Sketch state is in-memory: error guarantee, zero population, bucket vector, min, max, sum, and total population. No persistence is built in, but `getSamples` exposes bucket counts for telemetry export.

## Dependencies and Integration Points
It depends on standard math/vector algorithms and Flow `ASSERT`/unit-test support. `Stats.cpp` uses `DDSketch<double>` for latency samples and transport peers use sketches for ping/connect latencies.

## Risks and Edge Cases
The base class treats values below `1e-18` as zero and asserts huge values stay within allocated buckets. `DDSketch<T>` static-asserts little-endian systems. Bucket counters are `uint32_t`, so extremely long-lived sketches can overflow per bucket. `DDSketchSlow` references `DDSketch<T>::EPS` in its offset expression, which is equivalent through the base constant but visually odd.

## Test Signals
`BenchSamples.cpp` benchmarks all three major usage patterns. Accuracy tests elsewhere should check percentile error bounds, merge behavior, zero handling, and min/max/sum after clear.
