# sources/test-tools/syzkaller/pkg/report/title_stat.go

## Purpose

`title_stat.go` maintains a JSON trie of crash-report title sequences. It lets report processing accumulate how often one report title is followed by later titles in the same report set, which is useful for understanding chains of warnings or repeated crash signatures.

## Important APIs, Types, And Functions

`AddTitleStat(file string, reps []*Report) error` extracts report titles, reads the existing stat file, updates counts, and writes JSON through `osutil.WriteJSON`. `ReadStatFile` returns an empty `titleStat` for missing files or decodes JSON otherwise. `titleStat` stores `Count` and nested `Nodes`; `titleStat.add` recursively increments prefix counts; `titleStat.visit` walks leaves and invokes a callback with count and title chain.

## Control Flow, State, Dependencies, And Risks

The update path is read-modify-write with no locking, so concurrent writers could lose increments. Empty report lists are ignored. Counts live only in the JSON file named by the caller. The code depends on `osutil.IsExist`, `ReadJSON`, `WriteJSON`, and Go 1.23-style `maps.Keys` iteration; traversal order is intentionally map-defined unless callers sort. Risks are corrupted JSON, non-atomic multi-process updates, and hidden nondeterminism in `visit` ordering.

## Test Signals

`title_stat_test.go` covers missing files, single-title chains, two-title chains, and branching chains sharing a prefix. Extra useful tests would cover malformed JSON and repeated updates from multiple independent calls.
