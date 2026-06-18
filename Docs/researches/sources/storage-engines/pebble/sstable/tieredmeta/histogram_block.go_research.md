# sources/storage-engines/pebble/sstable/tieredmeta/histogram_block.go

## Purpose
Encodes and decodes tiering histogram metadata blocks for SSTables and blob files, including per-span histograms and per-SSTable summary counters.

## Important APIs, Types, And Functions
`KindAndTier` enumerates histogram categories. `Key` combines kind and `TieringSpanID` with encode/decode helpers. `TieringHistogramBlockWriter` supports `Add`, `AddKeyBytes`, `AddHotAndColdBlobRefBytes`, `IsEmpty`, `Finish`, and reset. `SSTableSummary` stores summary counters. `DecodeTieringHistogramBlock` decodes summary and histogram map.

## Control Flow
The writer lazily creates one `histogramWriter` per `(kind, spanID)`, records bytes, separately accumulates summary fields, sorts keys by kind/span ID, encodes them into a columnar key-value block, prefixes summary varints, then resets itself. Decoding reads three summary varints and iterates the columnar key-value block to decode keys and histograms.

## State And Persistence Behavior
The finished byte slice persists in table/blob metadata. Writer state is transient and reusable after `Finish`.

## Dependencies And Integration Points
Depends on `colblk.KeyValueBlockWriter/Decoder`, tiering base types, `StatsHistogram`, and map/slice sorting helpers. It supports future compaction/tiering decisions using persisted metadata.

## Risks And Edge Cases
Key decode rejects too-short or invalid kind values. Empty writers still encode summary zeros plus an empty histogram block if `Finish` is called. Sorting determines deterministic persisted bytes.

## Test Signals
Randomized tests validate summary counters, presence of every expected key, and decoded histogram aggregate fields.
