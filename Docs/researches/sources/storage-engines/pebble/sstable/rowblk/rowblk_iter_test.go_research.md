# sources/storage-engines/pebble/sstable/rowblk/rowblk_iter_test.go

## Purpose
Tests row-block iteration semantics for both `RawIter` and internal-key `Iter`, including restart intervals, ordering, prefix compression, key stability, direction changes, and synthetic key transforms.

## Important APIs, Types, And Functions
`blockIterInternalIterator` adapts `Iter` to `base.InternalIterator` for `itertest.RunInternalIterCmd`. `TestInvalidInternalKeyDecoding` verifies malformed internal keys decode to invalid trailers. `TestBlockIter` tests `RawIter` seek/forward/reverse behavior against a hand-encoded block. `TestBlockIter2` uses datadriven commands to build blocks at restart intervals 1 through 4 and exercise iterator commands. `TestBlockIterKeyStability`, `TestBlockIterReverseDirections`, `TestBlockSyntheticPrefix`, `TestBlockSyntheticSuffix`, and `TestIsLowerBoundRand` cover important iterator contracts.

## Control Flow And State
Tests construct row blocks with `Writer`, open iterators with no transforms or synthetic prefix/suffix transforms, and compare returned `InternalKV` sequences against an equivalent block with transformed keys materialized on disk. The synthetic suffix tests intentionally seek around original suffixes, replacement suffixes, in-between suffixes, suffixless keys, exhausted iterators, and direction changes. The randomized lower-bound test generates sorted key sets and random transforms, then checks that `IsLowerBound` has no false positives.

## Persistence And Integration
The tests persist only transient encoded blocks in memory. They integrate with `datadriven` testdata, `itertest`, `testkeys.Comparer`, `blockiter.Transforms`, and `require` assertions. The key-stability test inspects unsafe pointer ranges to ensure restart-interval-1 user keys are backed by the original block bytes.

## Risks
Coverage is broad for transform and seek behavior, but the tests use in-memory blocks and do not directly cover corrupt restart tables, checksum boundaries, lazy value-block retrieval, or very large block offsets. Randomized tests depend on logged seeds for reproduction.

## Test Signals
This file is itself the primary semantic signal for `rowblk.Iter`. It also acts as regression coverage for a previous reverse-to-forward bug where `fullKey` was not restored after reverse iteration.
