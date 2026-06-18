# sources/test-tools/syzkaller/prog/heatmap.go

Purpose: defines mutation heatmaps that bias byte mutations toward non-uniform data regions.

Important APIs/types/functions: `Heatmap` interface, `MakeGenericHeatmap`, `GenericHeatmap.NumMutations`, `GenericHeatmap.ChooseLocation`, `segment`, `calculateLengthAndSegments`, and `translateIdx`.

Control flow and state: construction splits data into 64-byte chunks, groups contiguous chunks that are not a single repeated byte into segments, and falls back to one full-data segment if all chunks are constant. `ChooseLocation` selects uniformly within concatenated interesting segments and translates back to raw index. `NumMutations` uses random counts based on heatmap length, with a hard cap of 10.

Dependencies and integration: uses `math/rand`; intended for mutating large blobs/images where uniform random byte selection wastes effort on padding or constant areas.

Risks: panics on empty data and out-of-range translated indexes. Granularity can skip small interesting changes inside otherwise constant chunks or include noise in mixed chunks. Mutation count is randomized and heuristic.

Test signals: `heatmap_test.go` decodes representative base64 data and asserts chosen indexes stay within expected interesting regions, including all-constant fallback.
