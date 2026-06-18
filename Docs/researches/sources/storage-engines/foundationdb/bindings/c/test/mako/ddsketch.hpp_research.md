# sources/storage-engines/foundationdb/bindings/c/test/mako/ddsketch.hpp

## Purpose
Header-only DDSketch implementations for approximate latency/value distributions in Mako stats.

## Important APIs, types, and functions
`fastLogger::fastlog/reverseLog`, `DDSketchBase`, `DDSketch<T>`, `DDSketchSlow<T>`, and `DDSketchFastUnsigned` provide add, percentile, mean, min/max, clear, and merge behavior.

## Control flow
`addSample` maps positive samples to logarithmic buckets and near-zero samples to a zero counter. `percentile` scans buckets upward or downward based on percentile. `mergeWith` combines compatible bucket arrays.

## State and persistence behavior
State is in-memory aggregate counts, zero count, population size, min, max, and sum. No serialization is implemented.

## Dependencies and integration points
Uses standard math/vector/assertions and endian/compiler intrinsics. Consumed by Mako statistics code.

## Risks and test signals
Negative/out-of-range values and incompatible merges are assertion-guarded. Percentile accuracy depends on mapping constants; stats output is the practical signal.
