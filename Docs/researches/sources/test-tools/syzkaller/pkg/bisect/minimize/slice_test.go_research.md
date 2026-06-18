# sources/test-tools/syzkaller/pkg/bisect/minimize/slice_test.go

Purpose: Tests and benchmarks for the generic slice minimizer.

Important APIs/types/functions: `TestBisectSliceToZero`, `TestBisectSliceFull`, `TestBisectSliceWithFixed`, `TestBisectRandomSlice`, `BenchmarkSplits`, and `runMinimize`.

Control flow: The deterministic tests build integer arrays and predicates for no-needed-elements, all-needed-elements, and fixed-element cases. The randomized test selects a random subset of non-zero guilty elements and asserts the minimizer returns exactly those elements while keeping predicate calls below a logarithmic bound. The benchmark measures remaining elements after a fixed number of predicate calls.

State and persistence behavior: Uses in-memory arrays and randomized sources from `testutil.RandSource` or wall-clock benchmark seed. No file or external persistence.

Dependencies/integration points: Integrates with `pkg/testutil` for iteration/randomness and `testify/assert` for assertions.

Risks: Benchmark randomness from `time.Now().UnixNano()` makes exact performance numbers non-reproducible. The randomized test validates monotonic predicates but not adversarial non-monotonic behavior, which the minimizer does not promise to support.

Test signals: Strong coverage for basic behavior, fixed element preservation, output minimality for generated monotonic predicates, and rough predicate-call complexity.
