# sources/test-tools/syzkaller/pkg/bisect/minimize/slice.go

Purpose: Generic slice minimization helper for finding a small subsequence that still satisfies a predicate. It is intended for expensive bisection predicates and tries to reduce predicate calls while preserving element order.

Important APIs/types/functions: `Config[T]` carries `Pred`, `MaxSteps`, `MaxChunks`, and `Logf`. `Slice` minimizes all elements. `SliceWithFixed` keeps fixed elements while minimizing only free indices. `sliceCtx`, `arrayChunk`, `ErrTooManyChunks`, `bisect`, `splitChunks`, `initialSplit`, `predRun`, `done`, `elements`, `chunkInfo`, `mergeChunks`, `mergeRawChunks`, and `splitChunk` implement the algorithm.

Control flow: `Slice` starts with one chunk and calls `bisect`. The first split may divide into three or `MaxSteps` chunks, then later passes split surviving chunks in two. For every candidate sub-chunk, `predRun` tests whether the remainder still satisfies `Pred`; if yes, the candidate is dropped. Chunks that cannot be split further become final. `SliceWithFixed` maps original indices into free/fixed sets, runs `Slice` on free indices, then merges fixed elements back in original order.

State and persistence behavior: State is in-memory only: current chunk list and predicate run count. `MaxSteps` is a soft budget that makes future predicates behave as false, returning an intermediate result. `MaxChunks` returns `ErrTooManyChunks` plus the current valid but not fully minimized result.

Dependencies/integration points: Uses only Go standard library packages. It is reusable across bisection/minimization callers that can express success as `Pred([]T)`.

Risks: Correctness assumes a monotonic predicate: if a set satisfies `Pred`, supersets also satisfy it. Non-monotonic predicates may produce misleading minima. `SliceWithFixed` returns `nil, err` on minimization errors, losing the intermediate free result except for `ErrTooManyChunks` currently propagated as an error. `MaxSteps` can intentionally stop before true minimality.

Test signals: Covered by `slice_test.go`, including zero/full minimization, fixed elements, randomized subset preservation, and benchmark behavior under a predicate-call limit.
