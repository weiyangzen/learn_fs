# sources/storage-engines/pebble/sstable/tieredmeta/histogram_test.go

## Purpose
Randomized tests for tiering histogram block and individual histogram encoding/decoding.

## Important APIs, Types, And Functions
`expectedStats`, `generateRandomRecords`, and `requireStatsEqual` are helpers. `TestHistogramBlock_Randomized` tests full block encode/decode. `TestHistogramEncoding_Roundtrip` tests individual histogram writer round trips.

## Control Flow
Tests create random spans, kinds, attributes, byte counts, key-byte summaries, and hot/cold blob reference bytes. They record expected aggregate totals while writing histograms, encode, decode, and compare summary plus every histogram's total/count/no-attribute accounting.

## State And Persistence Behavior
All state is in memory. Encoded byte slices model persisted tiering metadata blocks.

## Dependencies And Integration Points
Depends on `base.TieringSpanID`, `base.TieringAttribute`, `testutils.RandIntInRange`, `TieringHistogramBlockWriter`, and `DecodeStatsHistogram`.

## Risks And Edge Cases
Random seeds use current time, so failure reproduction requires captured seed/logging not currently present. Tests assert aggregate accounting, not t-digest quantile accuracy.

## Test Signals
Signals are successful decode, matching summary counters, expected histogram map length, and exact aggregate fields for every histogram.
