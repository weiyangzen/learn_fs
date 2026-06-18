# sources/sync-backup/kopia/repo/content/index/one_use_index_builder.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/one_use_index_builder.go_research.md`.

Purpose: memory-oriented builder used for epoch index compaction where sorted output is needed once and the builder can be drained as it builds.

Important APIs: `OneUseBuilder` wraps an LLRB tree. `NewOneUseBuilder`, `Add`, `Length`, `sortedContents`, `shard`, and `BuildShards` mirror the regular builder API enough for compaction. `Info.Less` provides tree ordering by `ContentID`.

Control flow: `Add` replaces existing entries only if the new `Info` wins by the merged precedence rule. `sortedContents` repeatedly deletes the tree minimum, intentionally emptying the builder. `shard` also drains the tree, assigning items by FNV hash of `ContentID.String()`. `BuildShards` serializes each shard through `buildSortedContents` and optionally appends random uniqueness bytes.

State and persistence behavior: this builder is destructive by design. After sorting or sharding, `Length` becomes zero. Persisted output is the same v1/v2 binary index format as the regular builder.

Dependencies: `petar/GoLLRB/llrb`, `gather`, crypto randomness, FNV, and shared index builders.

Risks and tests: callers must not reuse it after sorting/sharding. Shard distribution must match regular builder semantics. `packindex_test.go` validates sorted order, stable output equivalence, shard counts, and that the builder is drained after sharding.
