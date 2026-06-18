# sources/sync-backup/kopia/repo/splitter/splitter_pool.go

Purpose: wraps splitter factories with `sync.Pool` reuse to reduce allocations in hot write paths.

Important APIs/types/functions: `recyclableSplitter` embeds a `Splitter` and its pool. Its `Close` resets, closes, and returns the underlying splitter to the pool. `pooled(f Factory)` returns a factory that gets splitters from the pool or creates new ones.

Control flow: pooled factory checks `pool.Get`; nil creates `recyclableSplitter{f(), pool}`, non-nil wraps the retrieved splitter. `Close` is the return-to-pool hook.

State and persistence behavior: in-memory object pooling only; no persisted data. Reused splitter state is reset before pooling.

Dependencies/integration: used for registered modern splitter factories in `splitter.go`; object writers must call `Close` to return splitters.

Risks: if callers forget `Close`, pooling is ineffective. Returning a splitter while still in use would corrupt chunking state, but normal writer ownership prevents that. Type assertion assumes only `Splitter` values are placed in the pool.

Test signals: splitter stability tests run pooled variants twice to detect state leakage through reuse.
