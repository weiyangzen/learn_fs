# sources/sync-backup/kopia/repo/content/committed_content_index.go

Purpose: manages the set of committed content indexes currently in use by a repository reader, including cache population, index merging, deleted-content filtering, small-index combination, revision tracking, and cache expiry.

Important APIs/types/functions: `committedContentIndex`, `committedContentIndexCache`, `smallIndexEntryCountThreshold`, `getContent`, `addIndexBlob`, `listContents`, `use`, `combineSmallIndexes`, `fetchIndexBlobs`, `missingIndexBlobs`, and `newCommittedContentIndex`.

Control flow: loading starts by identifying missing index blobs, fetching them in parallel, caching them, and then `use` merges the requested active index blob set. `merge` reuses already-open indexes, opens missing ones from cache, optionally skips bad cache entries in permissive mode, combines small indexes into one in-memory segment, and returns a new merged view. `use` swaps the active map, increments revision, closes indexes no longer active, and asks the cache to expire unused entries.

State and persistence behavior: active index state is protected by `mu`; `rev` is atomic and increments after content visibility changes. Cache state may be memory-only or disk-backed under `<cache>/indexes`. `deletionWatermark` filters deleted entries whose deletion timestamp is not after the watermark.

Dependencies/integration: used by `SharedManager` to answer content lookup/listing. Depends on index builders/openers, format provider mutable parameters, gather buffers, blob IDs, content logging, and clock/cache options.

Risks and edge cases: revision increments must happen after visibility updates or callers can cache inconsistent results. Combining small indexes must preserve entry ordering and close newly opened indexes on errors. Permissive cache loading can hide corrupt/missing index blobs and should only be used deliberately.

Test signals: cache tests verify cache implementations used by this manager; broader content manager tests cover lookup/listing. Direct tests should cover deleted watermark behavior, small-index combination, revision changes, and permissive open failures.
