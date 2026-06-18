# sources/storage-engines/foundationdb/fdbrpc/DDSketchTest.cpp

## Purpose
`DDSketchTest.cpp` contains unit/performance-style tests for the fdbrpc `DDSketch` approximate percentile data structure.

## Important APIs, Types, and Functions
The file imports `fdbrpc/DDSketch.h`, defines `forceLinkDDSketchTests`, and declares test cases `/fdbrpc/ddsketch/accuracy` and `/fdbrpc/ddsketch/correctness`. It uses `DDSketch<double>::addSample` and `percentile`.

## Control Flow
The accuracy test runs 100 trials of one million skewed samples, stores exact values, sorts them, compares selected percentiles against `DDSketch`, accumulates relative error, and prints average errors. The correctness test adds 4000 small positive samples and asserts common percentiles are positive and finite.

## State and Persistence Behavior
All state is transient test memory. The tests do not persist data or modify external state.

## Dependencies and Integration Points
It depends on Flow unit tests, deterministic random sampling, `<limits>`, `<random>`, and `DDSketch`. The `forceLink` function ensures the tests are retained by the linker.

## Risks and Edge Cases
The accuracy test is computationally heavy due to 100 million generated values and sorting one million values per trial. It prints error statistics but does not assert an accuracy threshold, so regressions could be visible only in logs. Correctness only checks positive finite outputs, not exact rank guarantees.

## Test Signals
Passing correctness proves nonzero percentile outputs for a representative positive range. Accuracy logs give diagnostic signals for relative error at extreme and central percentiles.
