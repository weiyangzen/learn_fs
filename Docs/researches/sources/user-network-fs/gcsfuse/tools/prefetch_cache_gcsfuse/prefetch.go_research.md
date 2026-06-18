# sources/user-network-fs/gcsfuse/tools/prefetch_cache_gcsfuse/prefetch.go

Purpose: downloads objects from a GCS bucket into the local content cache format used by gcsfuse.

Important APIs/types/functions: `NUM_WORKERS`, `downloadFile`, and `prefetchCache`.

Control flow: `prefetchCache` creates a storage client and 10-minute context, lists objects with optional prefix, sends object attrs through a channel, and runs 10 worker goroutines. Each worker creates a temp cache file, streams object bytes into it, and writes adjacent JSON metadata containing cache file name, bucket, object, generation, and metageneration.

State/persistence behavior: creates cache data files and `.json` metadata files in the cache directory. It reads object data and metadata from GCS.

Dependencies/integration: depends on `cloud.google.com/go/storage` and internal `contentcache.CacheFileObjectMetadata`/prefix conventions.

Risks/test signals: partial data files are not removed on copy or metadata failure, matching TODO comments. Listing errors only log and stop the producer; `prefetchCache` still returns nil after worker completion.
