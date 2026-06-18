# sources/sync-backup/kopia/repo/blob/sharded/sharded_test.go

Purpose: verifies sharded storage layout compatibility, path mapping, prefix listing, malformed parameter handling, and parameter cloning using filesystem-backed storage.

Important APIs/types/functions: tests include `TestShardedOpenLegacyFileStorage`, `TestShardedOpenLatestFileStorage`, `TestShardedFileStorage`, `TestShardedFileStorageShardingMap`, `TestShardedFileStorageShardingMap_Invalid`, and `TestClone`.

Control flow: legacy/latest tests open filesystem storage with nil sharding options under create/open modes and assert expected `.f` paths. General storage tests run `blobtesting.VerifyStorage` across many shard specs and list parallelism values. Mapping tests write a custom `.shards` JSON file, upload blobs, assert exact file paths, and list every prefix. Malformed tests confirm bad `.shards` blocks operations until removed, then cached valid parameters tolerate later file corruption.

State and persistence behavior: tests create temp repositories with `.shards`, `.f` blob files, and ignored foreign files. Clone tests serialize before/after mutation to prove no shared slices.

Dependencies/integration: depends on filesystem provider, sharded package, gather buffers, blobtesting, and temp directories.

Risks and edge cases: default layout compatibility is important for existing repositories. Prefix listing must remain correct across nested shard directories and overrides.

Test signals: failures indicate path-layout regression, broken prefix filtering, unsafe parameter cache behavior, or shallow-copy bugs.
