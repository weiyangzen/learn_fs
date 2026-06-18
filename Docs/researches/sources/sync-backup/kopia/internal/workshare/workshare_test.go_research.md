<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/internal/workshare/workshare_test.go -->
# sources/sync-backup/kopia/internal/workshare/workshare_test.go

- Purpose: Tests workshare pool and async group using a recursive tree-sum workload.
- Important APIs/types/functions: `treeNode`, `buildTree`, `computeTreeSumRequest`, `dispatchComputeTreeSumRequest`, `computeTreeSum`, `TestComputeTreeSum10`, `TestComputeTreeSum1`, `TestComputeTreeSum0`, `TestComputeTreeSumNegative`, `TestDisallowed_DoubleWait`, `TestDisallowed_WaitAfterClose`, `TestDisallowed_UseAfterPoolClose`, `BenchmarkComputeTreeSum`.
- Control flow: Recursive work opportunistically shares child traversal when capacity is available, waits for async requests, and sums results. Panic tests verify invalid `AsyncGroup` and closed-pool usage.
- State and persistence: In-memory tree, worker pool, and async request structs.
- Dependencies and integration points: Uses `testify/require`.
- Risks and edge cases: Does not test close racing with active producers beyond explicit closed-pool misuse.
- Test signals: Direct coverage for workshare pool/group semantics.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/internal/workshare/workshare_test.go -->
