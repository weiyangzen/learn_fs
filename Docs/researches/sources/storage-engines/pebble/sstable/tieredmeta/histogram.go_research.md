# sources/storage-engines/pebble/sstable/tieredmeta/histogram.go

## Purpose
Implements tiering statistics histograms using t-digest sketches to estimate byte distributions by `base.TieringAttribute`.

## Important APIs, Types, And Functions
`digestDelta` configures t-digest compression. `StatsHistogram` stores total bytes/count, no-attribute bytes, and a digest. Methods include `CDF`, `Quantile`, `BytesWithAttr`, `BytesBelowThreshold`, `BytesAboveThreshold`, `encode`, `DecodeStatsHistogram`, and `Merge`. `histogramWriter`, `makeHistogramWriter`, `record`, and `encode` build histograms.

## Control Flow
Writers record `(attribute, bytes)` values, counting attribute zero separately and adding non-zero attributes to the digest weighted by bytes. Encoding writes varints for totals/no-attr/digest size followed by serialized digest data. Decoding reverses the process and validates digest size.

## State And Persistence Behavior
Encoded histograms persist inside tiering histogram blocks. In-memory digest state is mergeable for aggregating file-level statistics.

## Dependencies And Integration Points
Used by `TieringHistogramBlockWriter` and decoding paths in `histogram_block.go`. Depends on `tdigest`, Pebble `base`, binary varints, and corruption errors.

## Risks And Edge Cases
Attribute zero is excluded from digest calculations by design. Decode distinguishes corruption for malformed varints from digest-size mismatch errors. Quantile/CDF accuracy is approximate and controlled by digest compression.

## Test Signals
Histogram round-trip tests verify totals, counts, and zero-byte accounting. Randomized block tests exercise encoded histograms through the block wrapper.
