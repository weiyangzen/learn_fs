## sources/sync-backup/restic/internal/repository/index/index_parallel.go

Purpose: parallel loader for all repository index files.

Important APIs: `ForAllIndexes(ctx, lister, repo, fn)` lists `restic.IndexFile` entries, loads each via `LoadUnpacked`, decodes with `DecodeIndex`, and invokes `fn(id, idx, err)`.

Control flow and state: worker count is `repo.Connections() + GOMAXPROCS`, reflecting mixed I/O/CPU decode cost. The callback is serialized with a mutex even though loading/decoding is parallel. Returning an error from the callback cancels/propagates through `restic.ParallelList`.

Dependencies and integration points: used by master index loading, debug index dumping, repository checker, and streaming index listing.

Risks and test signals: serialized callback prevents races in callers but can bottleneck heavy callback work. Decode errors are passed to the callback rather than immediately stopping, allowing callers like checker to collect per-index errors. Tests cover loading all expected fixture indexes and callback error propagation.
