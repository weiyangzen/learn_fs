<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/cache_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/cache_test.py

Purpose: unit/regression tests for ad-hoc file cache behavior and repository chunkindex cache helpers.

Important APIs: `AdHocWithFilesCache`, `FileCacheEntry`, `delete_chunkindex_cache`, `read_chunkindex_from_repo_cache`, `ChunksMixin`, `write_chunkindex_to_repo_cache`, `list_chunkindex_hashes`, `ChunkIndex`, `ChunkIndexEntry`, `Statistics`, `Manifest`, `Repository`, `AESOCBKey`, `safe_ns`, and `int_to_timestamp`.

Control flow: class fixtures create a real temporary repository, key, manifest, and cache. Tests verify manifest chunk is not treated as seen, chunk add/reuse returns sizes, file-known lookup leaves empty files cache, and no-change backups preserve current files cache entries when `_newest_cmtime` is `None`. Standalone tests cover missing chunkindex cache deletion/read handling and ensure `ChunksMixin.chunks` binds fragmented repository indexes without consolidating cache fragments.

State and persistence: writes repository chunks, manifests, compressed files-cache entries, and cache/chunks fragments. Some tests monkeypatch repository store methods to simulate races.

Dependencies/integration: depends on repository store cache layout, chunk index serialization, cache integrity metadata, and key/manifest setup. Risks include cache entry loss after no-change backups, races deleting missing cache objects, and costly cache fragment consolidation on read. Test signals are returned tuples, cache dictionaries, absence of raised exceptions, fragment counts, and in-memory index membership.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/cache_test.py -->
