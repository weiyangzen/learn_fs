# sources/sync-backup/kopia/repo/object/object_manager.go

Purpose: manages content-addressable repository objects on top of content storage, including writer creation, object concatenation, and backing-content prefetch.

Important APIs/types/functions: `Reader`, internal `contentReader`/`contentManager`, `Manager`, `NewWriter`, `closedWriter`, `Concatenate`, `appendIndexEntriesForObject`, `appendIndexEntries`, `PrefetchBackingContents`, and `NewObjectManager`.

Control flow: `NewWriter` reuses an `objectWriter` from a pool, selects configured or default splitter, configures compression, prefix, async write semaphore, and resets buffers. `Concatenate` converts each input object into indirect index entries, writes a new indirect index object, and returns an indirect object ID. Prefetch walks backing contents for object IDs, ignores not-found errors, and asks the content manager to prefetch collected IDs.

State/persistence behavior: writers persist split contents through the content manager; concatenation persists only a new indirect index object rather than rewriting source data. The manager stores default splitter factory and a writer pool.

Dependencies/integration: integrates content manager read/write APIs, compression registry, splitter registry, object index loading/writing, metrics placeholder, and content prefetching.

Risks/test signals: pooled writers must be fully reset to avoid leaking prior state; concatenation relies on correct lengths and offsets, with a small deduplication cost at externally chosen split boundaries. Errors while opening component objects abort concatenation. Tests likely live in neighboring object files not in this subset.
