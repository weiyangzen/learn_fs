# sources/test-tools/syzkaller/pkg/cover/cover.go

Purpose: defines the minimal in-memory coverage set abstraction over raw PCs.

Important APIs/types/functions: `Cover map[uint64]struct{}`, `FromRaw`, `Merge`, `MergeDiff`, and `Serialize`.

Control flow: `FromRaw` initializes a coverage set by merging raw PCs. `Merge` lazily allocates the map and inserts every PC. `MergeDiff` also lazily allocates, mutates the supplied raw slice in place to compact newly seen PCs, inserts them, and returns the new prefix. `Serialize` returns unsorted map keys.

State and persistence: state is only the mutable map held through the pointer receiver. No synchronization is provided.

Dependencies and integration: no external imports. Used wherever syzkaller wants deduplicated coverage PCs and incremental newly-covered signals.

Risks: `MergeDiff` overwrites the input slice, which is documented but easy to misuse. `Serialize` order is nondeterministic and callers must sort if stable output is needed. The type is not concurrent-safe.

Test signals: `cover_test.go` checks nil inputs, merging, diff compaction, and sorted serialized results.
