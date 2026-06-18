# sources/test-tools/syzkaller/tools/syz-imagegen/combinations.go

Purpose: this Linux-only helper computes representative parameter combinations for filesystem image generation, either all combinations or a bounded covering array.

Important APIs and flow: `CoveringArray(params, n)` incrementally extends rows by parameter. If all combinations fit within `n` or `n == 0`, it performs full cartesian expansion. Otherwise it uses `pairCoverage` to choose values that maximize newly covered pairs, then triples, and duplicates rows until reaching `n` or no additional coverage is gained. Rows are sorted deterministically and converted from value indexes to strings. `rowToPairCombos` emits pair or triple coverage keys, also adding a value-diversity singleton encoded in `third`. `extendRow` clones before append.

State and persistence: pure in-memory algorithm, no IO.

Dependencies and integration: used by `imagegen.go` to reduce huge mkfs flag spaces while preserving broad pair/triple coverage.

Risks: greedy algorithm is deterministic but not guaranteed minimal or globally optimal. Empty params return no rows. The synthetic singleton coverage uses `newID+1` positions to avoid zero values but is internal only.

Test signals: `combinations_test.go` fixes behavior for full binary combinations and a bounded pairwise case.
