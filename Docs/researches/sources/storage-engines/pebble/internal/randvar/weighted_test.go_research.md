# sources/storage-engines/pebble/internal/randvar/weighted_test.go

## Purpose
This test is a smoke test for the `Weighted` random variable generator. It ensures repeated calls to `Int` do not panic for a representative weight vector that includes a zero-weight index.

## Important APIs, Types, and Functions
`TestWeighted` calls `NewWeighted(nil, 1, 2, 2, 0, 3)`, draws 10,000 integers through `w.Int()`, and calls package test helper `dumpSamples` only when `testing.Verbose()` is true.

## Control Flow and State
The test relies on `NewWeighted` defaulting nil RNGs through `ensureRand`. It accumulates generated indexes into a local slice but does not inspect them unless verbose output is requested.

## Dependencies and Integration
It depends only on `testing` directly, plus package-local helpers. It is part of the broader `randvar` test suite and can be useful while manually inspecting distribution shape, but it is not a statistical validation.

## Risks and Gaps
Because there are no assertions, this test catches only panics and gross infinite-loop-style failures. It would not catch a biased distribution, zero-weight selection, empty input returning `-1`, or mutation of the weights slice after construction.

## Test Signals
The presence of the zero weight in the sample vector is a weak signal that zero weights are expected to be tolerated. There is no stable seed asserted in this file, so verbose output is diagnostic rather than golden.
