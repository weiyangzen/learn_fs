<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/contentcache/contentcache_test.go -->
# Research: sources/user-network-fs/gcsfuse/internal/contentcache/contentcache_test.go

Purpose: tests content-cache metadata validation, checkpoint JSON round-trip, and basic thread-safety for add/replace, get, and remove operations.

Important APIs/types/functions: constants `numConcurrentGoRoutines`, `testTempDir`, generation/metageneration constants; tests `TestValidateGeneration`, `TestValidateGenerationNegative`, `TestReadWriteMetadataCheckpointFile`, `TestContentCacheAddOrReplace`, `TestContentCacheGet`, and `TestContentCacheRemove`.

Control flow: validation tests construct `CacheObject` values with metadata and compare generation/metageneration inputs. Checkpoint testing creates an anonymous file, writes metadata JSON, reads it back, unmarshals, and compares fields. Concurrency tests spawn 100 goroutines against a shared `ContentCache`: repeated `AddOrReplace` on one key, repeated `Get` of one cached object, and parallel `Remove` across many keys.

State and persistence: writes temporary cache metadata under `/tmp` and cache files through `os.CreateTemp`/anonymous files. Tests remove only the explicit metadata file in the checkpoint test; Add/Replace and Remove paths are expected to clean up through cache object destruction where applicable.

Dependencies and integration points: uses `contentcache`, `fsutil.AnonymousFile`, `timeutil.RealClock`, `sync.WaitGroup`, ogletest, and local `/tmp`. It validates the local content cache used by file inodes when local file caching is enabled.

Risks: tests use `/tmp` globally rather than `t.TempDir`, so leftovers or permissions could interfere. They do not test `RecoverCache`, corrupt metadata, missing cache files, or descriptor limits. The comment on `TestContentCacheAddOrReplace` says it should panic on concurrent map access, but the current assertion expects no panic/error because the implementation is mutex-protected.

Test signals: useful regression coverage for mutex-protected map access and metadata checkpoint formatting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/contentcache/contentcache_test.go -->
