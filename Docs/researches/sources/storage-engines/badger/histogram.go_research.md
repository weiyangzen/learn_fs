# sources/storage-engines/badger/histogram.go

## Purpose
`histogram.go` builds and prints key-size and value-size histograms for a Badger database, optionally restricted to a key prefix.

## Important APIs, Types, and Functions
- `(*DB).PrintHistogram(keyPrefix)`: user-facing printer that handles nil DB and prints key/value histograms.
- `histogramData`: stores bin upper bounds, per-bin counts, total count, min/max, and sum.
- `sizeHistogram`: groups key and value histograms.
- `newSizeHistogram`: initializes key bins from `2^1` through `2^16` and value bins from `2^1` through `2^30`.
- `createHistogramBins`: builds power-of-two bin boundaries.
- `(*histogramData).Update`: updates min/max/sum/count and assigns a value to the first bin with `value < bound`, or overflow.
- `(*DB).buildHistogram`: scans a read transaction iterator and updates key/value sizes.
- `histogramData.printHistogram`: prints totals, min, max, mean, and non-empty ranges.

## Control Flow and State
`buildHistogram` creates a read-only transaction and iterator, seeks to the prefix, and loops while `ValidForPrefix` is true. Each item contributes `Item.KeySize()` and `Item.ValueSize()` without necessarily materializing full values. Printing walks non-empty bins and formats half-open ranges.

## Persistence Behavior
No persisted state is changed. The function reads a snapshot through a Badger transaction.

## Dependencies and Integration Points
Depends on `DB.NewTransaction`, iterators, item size methods, `fmt`, and `math`. It integrates with CLI/diagnostic usage that wants size distribution insight.

## Risks and Edge Cases
`printHistogram` divides by `totalCount`; empty databases or prefixes can produce `NaN` mean and min/max initialized to extreme values. Bin assignment uses strict `<`, so exact powers of two fall into the next bin.

## Test Signals
`histogram_test.go` validates same-size and mixed-size key/value distributions, counts, sums, min/max, and bin allocation for small values.
