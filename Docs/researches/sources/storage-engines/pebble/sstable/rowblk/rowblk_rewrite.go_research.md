# sources/storage-engines/pebble/sstable/rowblk/rowblk_rewrite.go

## Purpose
Provides a reusable row-block rewriter that replaces a point-key suffix within one encoded row block while preserving trailers, values, restart interval behavior, and row-block encoding.

## Important APIs, Types, And Functions
`NewRewriter` creates a `Rewriter` with a comparer and restart interval. `Rewriter` owns reusable `Writer`, `Iter`, scratch key, and byte allocator state. `RewriteSuffixes(input, from, to)` returns the rewritten block plus the first and last rewritten internal keys.

## Control Flow And State
The rewriter initializes an `Iter` over the source block, pre-sizes writer buffers when possible, scans every key with `First`/`Next`, requires every key to be a SET, validates that each user-key suffix equals `from`, builds a scratch key with the same prefix and trailer but `to` suffix, validates keys under invariants, and writes the original in-place value through `Writer.Add`. It copies the first and last rewritten keys through `bytealloc.A` so returned span keys outlive the scratch buffer.

## Persistence And Integration
The function transforms one in-memory uncompressed row block into another. It is used by `sstable/suffix_rewriter.go` and `RawRowWriter.rewriteSuffixes` for fast whole-SST suffix replacement. It intentionally preserves raw v3 value-prefix bytes because the row-block iterator is not configured to interpret value prefixes in this path.

## Dependencies
Depends on `base.Comparer` for comparison, splitting, and validation; `rowblk.Iter` for decoding; `rowblk.Writer` for encoding; `bytealloc` for durable returned keys; and `blockiter.NoTransforms` for reading original on-disk keys.

## Risks
The source block must contain only SET keys whose suffix is exactly `from`; any other key kind or suffix aborts. Obsolete bits are not preserved as semantic metadata beyond the decoded trailer behavior exposed by `Iter`. Writer buffer reuse means callers must treat the returned block as owned until the next rewrite. Since the rewriter is per-block, table-level metadata and properties must be reconciled by the caller.

## Test Signals
The block rewriter is exercised indirectly by `suffix_rewriter_test.go`, especially the by-block rewrite path that compares rewritten SST properties and, when formats match, byte-for-byte output against the reader/writer loop.
