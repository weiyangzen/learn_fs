# sources/sync-backup/kopia/repo/content/committed_content_index_disk_cache.go

Purpose: disk-backed implementation of `committedContentIndexCache` for cached committed index blobs.

Important APIs/types/functions: `diskCommittedContentIndexCache`, `simpleIndexSuffix`, `indexBlobPath`, `openIndex`, `hasIndexBlobID`, `addContentToCache`, and `expireUnused`.

Control flow: index blobs map to `<cache>/<blobID>.sndx`. `addContentToCache` skips if the file exists, otherwise writes bytes to an atomic temp file and renames it into place, tolerating races if another process created the file. `openIndex` mmaps the file through platform-specific `mmapFile` and opens an index with an unmap closer. `expireUnused` lists `.sndx` files, removes currently used IDs, and deletes remaining files only when older than `minSweepAge`.

State and persistence behavior: persists raw index bytes as `.sndx` files under the cache directory. Expiry is age-gated to avoid deleting indexes another process may have just created.

Dependencies/integration: used by `newCommittedContentIndex` when `CachingOptions.CacheDirectory` is set. Depends on atomic temp writes, mmap platform files, content logging, and index openers.

Risks and edge cases: concurrent writers rely on atomic rename and existence recheck. Expiry logging must tolerate files disappearing after directory listing. Platform-specific mmap close behavior is critical for FD usage and Windows file locking.

Test signals: cache tests cover add/open/expire and duplicate writes; Linux FD test ensures Unix mmap does not retain one file descriptor per open index.
