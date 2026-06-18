<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/contentcache/contentcache.go -->
# Research: sources/user-network-fs/gcsfuse/internal/contentcache/contentcache.go

Purpose: implements a disk-backed local content cache for GCS object bodies, with in-memory indexing and JSON checkpoint metadata so cache files can be recovered across process restarts.

Important APIs/types/functions: `CacheFilePrefix`, `CacheObjectKey`, `ContentCache`, `CacheFileObjectMetadata`, `CacheObject`, `ValidateGeneration`, `WriteMetadataCheckpointFile`, `Destroy`, `recoverFileFromCache`, `RecoverCache`, `matchPattern`, `New`, `NewTempFile`, `AddOrReplace`, `Get`, `Remove`, `NewCacheFile`, `recoverCacheFile`, and `Size`.

Control flow: `AddOrReplace` locks the cache, destroys any existing object for the key, creates a temp file under `tempDir`, wraps it as a cache file, writes a sibling JSON metadata checkpoint, stores a `CacheObject`, and returns it. `RecoverCache` defaults an empty temp dir to `/tmp`, scans directory entries, filters metadata filenames matching `gcsfusecache[0-9]+.json`, reads JSON, opens the referenced cache file, wraps it, and adds it to `fileMap`. `Remove` locks, destroys disk files and metadata, and deletes the map entry.

State and persistence: in-memory state is `fileMap` protected by a mutex. Persistent state is cache data files plus JSON metadata files storing bucket, object, generation, metageneration, and data filename. Cache validity is determined by generation/metageneration equality.

Dependencies and integration points: used by `fs.NewFileSystem` when `LocalFileCache` is enabled and by file inodes through `gcsx.TempFile`. Depends on `gcsx`, `logger`, `timeutil.Clock`, JSON, regexp, and local filesystem APIs.

Risks: recovery opens one descriptor per recovered file and has a TODO about descriptor scalability. `recoverFileFromCache` is not explicitly locked and is called from non-concurrent recovery. If writing metadata succeeds after data file creation but later operations fail, cleanup responsibility is limited. The file-level comment says not concurrent safe, while methods use a mutex; recovery remains non-concurrent.

Test signals: `contentcache_test.go` covers generation validation, metadata serialization, concurrent add/replace, concurrent get, and concurrent remove, but not recovery from corrupt/missing files.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/contentcache/contentcache.go -->
