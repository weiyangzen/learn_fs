# sources/sync-backup/kopia/repo/content/content_manager_iterate.go

Final split target: `Docs/researches/sources/sync-backup/kopia/repo/content/content_manager_iterate.go_research.md`.

Purpose: implements content and pack iteration over both uncommitted session state and committed indexes, including optional parallel callback execution and unreferenced pack discovery.

Important APIs and types: `IterateOptions` selects an `IDRange`, deletion visibility, and callback parallelism. `IterateCallback`, `IteratePackOptions`, `PackInfo`, and `IteratePacksCallback` define iteration contracts. `maybeParallelExecutor` fans callback work to worker goroutines. `snapshotUncommittedItems` builds a cloned overlay from `packIndexBuilder`, pending packs, and writing packs.

Control flow: `IterateContents` defaults to `index.AllIDs`, wraps the callback for optional parallelism, snapshots uncommitted items under the write-manager lock, filters by delete state and range, invokes callbacks for overlay records first, refreshes indexes if needed, then scans committed contents. If there is no overlay and all IDs including deleted are requested serially, it uses a fast path. `IteratePacks` groups visible `Info` records by pack blob and optionally preserves content details. `IterateUnreferencedPacks` builds a bigmap set of referenced pack IDs, expands prefixes if requested parallelism exceeds the prefix count, scans blob storage, and reports pack blobs absent from the used set.

State and persistence behavior: iteration is observational but must merge pending and committed views consistently. Deleted pending records can suppress committed records unless `IncludeDeleted` is set.

Dependencies: `bigmap`, `blob.IterateAllPrefixesInParallel`, content logging, blob prefix helpers, and the index range model.

Risks and tests: parallel callback errors are captured asynchronously, so callers may observe partial processing before cancellation. Unreferenced scans depend on prefix coverage. `content_manager_test.go` covers default, deleted, range, parallel, callback failure, and unreferenced-pack cases.
