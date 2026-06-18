# sources/storage-engines/pebble/internal/rangekeystack/user_iterator_test.go

## Purpose
This file tests the range-key user iterator stack, including merging semantics, defragmentation, randomized equivalence between fragmented and unfragmented inputs, and transform performance.

## Important APIs, Types, and Functions
`TestIter` uses datadriven `define` and `iter` commands over `keyspanimpl.MergingIter` with a coalescing transformer. `TestDefragmenting` drives `UserIteratorConfig.Init` against datadriven operations. `TestDefragmentingIter_Randomized` and `_FixedSeed` generate random range-key spans, fragment them, then compare iterator histories over random operations. Helpers include `fragment`, `debugContext`, and `runIterOp`. `BenchmarkTransform` measures `UserIteratorConfig.Transform` over varied key counts and suffix shadowing.

## Control Flow and State
Datadriven tests parse spans from text and execute explicit iteration commands. Randomized tests generate a keyspace, create original spans and deliberately fragmented equivalents, fragment both through `keyspan.Fragmenter`, initialize independent iterator stacks, run 100 random operations, and compare accumulated histories with diffs on failure. Benchmarks reuse `Buffers` and `UserIteratorConfig` between runs.

## Dependencies and Integration
The test imports `datadriven`, `keyspan`, `keyspanimpl`, `rangekey`, `testkeys`, `difflib`, and `testify/require`. It exercises integration between range-key coalescing, merging, bounds/defragmenting iteration, and test key comparers.

## Risks and Gaps
The randomized test uses time-based seeds for broad coverage and a fixed seed for reproducibility, but failures outside the fixed seed require captured logs. The benchmark uses internal-key mode for transform cost and does not assert allocations. Prefix-bound behavior is present in the config but not deeply highlighted in these tests.

## Test Signals
The core invariant is that a fragmented representation must iterate identically to the original after the stack merges and defragments it. The benchmark signals that transform performance under suffix shadowing is important.
