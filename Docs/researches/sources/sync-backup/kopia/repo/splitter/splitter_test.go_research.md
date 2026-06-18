# sources/sync-backup/kopia/repo/splitter/splitter_test.go

Purpose: validates deterministic chunk-boundary behavior for fixed, BuzHash, Rabin-Karp, and pooled splitters.

Important APIs/types/functions: `TestSplitterStability` drives all cases. Helpers `getSplitPoints`, `getSplitPointsByteByByte`, and `getSplitPointsRandomSlices` feed the same data in whole-slice, byte-by-byte, and random-slice modes.

Control flow: a deterministic random 5,000,000-byte buffer is generated. Each splitter factory is tested twice, possibly with reduced cases on constrained architectures. For each feeding mode, the test checks `MaxSegmentSize`, split count, average segment size, minimum split, and maximum split. Splitters are closed after use to test pool reset.

State and persistence behavior: no persistence, but expected stats encode the compatibility surface of chunking algorithms.

Dependencies/integration: depends on splitter factories and `testutil.ShouldReduceTestComplexity`.

Risks: exact numeric expectations are intentionally brittle; dependency updates to rollinghash or algorithm tweaks will fail tests and signal changed chunking behavior. Random-slice helper uses global `rand.Intn`, so test determinism depends on global seed stability for chunk feeding sizes, though split outcomes should be independent of input chunking.

Test signals: strong unit coverage for splitter determinism and state isolation across pooled reuse.
