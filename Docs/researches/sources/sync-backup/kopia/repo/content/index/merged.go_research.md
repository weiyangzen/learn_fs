# sources/sync-backup/kopia/repo/content/index/merged.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/index/merged.go_research.md`.

Purpose: implements an `Index` that merges multiple immutable index shards and resolves duplicate content IDs to the newest effective `Info`.

Important APIs: `Merged` is a slice of `Index` implementing `ApproximateCount`, `Close`, `GetInfo`, and `Iterate`. `contentInfoGreaterThanStruct` defines precedence: higher timestamp wins, then non-deleted beats deleted, then lexicographically higher pack blob ID wins for deterministic ties. Internal heap types drive sorted multi-index iteration.

Control flow: `GetInfo` queries every shard and keeps the best matching record. `Iterate` starts one goroutine per shard, reads sorted `Info` streams into a min-heap, coalesces duplicate content IDs, and emits only the best record for each ID. A `done` channel stops shard goroutines if the callback fails, and `Close` joins close errors from all shards.

State and persistence behavior: merged indexes are read-only views over existing shard bytes. The merge rule is the core state-conflict policy for delete/recreate and concurrent writer histories.

Dependencies: `container/heap`, sync, joined errors, and the index interface.

Risks and tests: goroutine lifetime must not outlive closed indexes, hence `wg.Wait` is deferred. Tie-breaking must be deterministic across shard order. `merged_test.go` covers range iteration, callback error propagation, empty merges, close, and all tie-breaker combinations.
