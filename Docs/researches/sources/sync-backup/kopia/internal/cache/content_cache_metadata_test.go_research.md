## sources/sync-backup/kopia/internal/cache/content_cache_metadata_test.go

Purpose: tests full-blob metadata cache mode.

Important APIs/types/functions: `TestContentCacheForMetadata` and `TestContentCacheForMetadata_Passthrough`.

Control flow, state, and persistence: creates a disk-backed cache storage through `BaseCacheDirectory`, fetches a whole blob and ranges, lists cache entries to confirm only one full-blob item is stored, closes the cache, and verifies passthrough behavior when base directory is empty.

Dependencies and integration points: exercises filesystem cache storage, `FetchFullBlobs`, and range extraction from cached full blobs.

Risks and test signals: validates whole-blob caching behavior but does not test invalid range handling in metadata mode directly beyond shared content cache tests.
