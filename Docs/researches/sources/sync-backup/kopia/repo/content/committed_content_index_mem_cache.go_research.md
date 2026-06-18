# sources/sync-backup/kopia/repo/content/committed_content_index_mem_cache.go

Purpose: in-memory implementation of `committedContentIndexCache` for repositories without a cache directory.

Important APIs/types/functions: `memoryCommittedContentIndexCache` holds a mutex-protected map from index blob ID to `index.Index`; methods implement `hasIndexBlobID`, `addContentToCache`, `openIndex`, and `expireUnused`.

Control flow: adding content opens an index directly from byte slices and stores it in the map. Opening returns the stored index or an error if absent. Expiry builds a new map containing only requested used IDs.

State and persistence behavior: all index data and opened index objects are memory-resident and lost when the process exits. Expiry immediately drops unused map entries.

Dependencies/integration: selected by `newCommittedContentIndex` when cache directory is empty. Depends on gather bytes and index openers.

Risks and edge cases: stored indexes are shared objects; close ownership is managed by the committed-content index. Re-adding an existing ID replaces the map entry without explicitly closing the old index.

Test signals: shared cache tests verify add/open/hit/expire behavior for memory cache.
