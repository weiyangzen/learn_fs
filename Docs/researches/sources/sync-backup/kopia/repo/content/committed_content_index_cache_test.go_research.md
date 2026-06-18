# sources/sync-backup/kopia/repo/content/committed_content_index_cache_test.go

Purpose: shared test suite for disk and memory committed-content-index cache implementations.

Important APIs/types/functions: `TestCommittedContentIndexCache_Disk`, `TestCommittedContentIndexCache_Memory`, `testCache`, `mustBuildIndex`, and `mustParseID`.

Control flow: the shared test verifies cache miss, failed open for missing index, adding an index, hit detection, duplicate add idempotency, opening indexes and reading expected pack IDs, closing opened indexes, expiring unused indexes, advancing fake time for disk cache safety, and confirming removed indexes are gone.

State and persistence behavior: disk cache stores `.sndx` files in a temp directory and uses fake time for sweep age; memory cache stores opened `index.Index` objects in a map.

Dependencies/integration: depends on content index builders, gather bytes, blob IDs, faketime, test logging, and both cache implementations.

Risks and edge cases: disk cache intentionally keeps young unused files until sweep age elapses. The test confirms duplicate writes are safe.

Test signals: failures indicate cache hit/miss, index serialization/opening, duplicate write, or expiry behavior has regressed.
