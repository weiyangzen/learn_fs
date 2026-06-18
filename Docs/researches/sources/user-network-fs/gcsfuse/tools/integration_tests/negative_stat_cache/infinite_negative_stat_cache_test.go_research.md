# sources/user-network-fs/gcsfuse/tools/integration_tests/negative_stat_cache/infinite_negative_stat_cache_test.go

Purpose: Defines the testify suite for infinite negative metadata stat cache behavior, specifically `--metadata-cache-negative-ttl-secs=-1`. It verifies that a path negatively cached as absent remains hidden from gcsfuse even after external creation in GCS, and that externally created directories can provoke `EEXIST` on later mkdir.

Important APIs/types/functions: `infiniteNegativeStatCacheTest` embeds `suite.Suite` and carries the active flag set plus randomized test directory. `SetupSuite` mounts using `testEnv.mountFunc`; `SetupTest` creates a unique `NegativeStatCacheTest...` directory; `TestInfiniteNegativeStatCache` uses `os.OpenFile`, `client.CreateObjectInGCSTestDir`, and error-string assertions; `TestAlreadyExistFolder` uses `os.Stat`, `client.CreateFolderInBucket` or `client.CreateObjectOnGCS`, and `os.Mkdir`; `TestInfiniteNegativeStatCacheTest` iterates config-built flag sets.

Control flow: each suite run mounts once, creates a fresh directory per test, exercises POSIX calls through the mount, mutates the bucket out of band, then asserts stale negative state. The runner short-circuits for pre-mounted GKE directories or loops over compatible config items otherwise.

State/persistence: test state is split between mounted filesystem paths and direct GCS objects/folders. Infinite negative cache is intentionally persistent across operations within the same mount. Teardown saves logs on failure and unmounts in suite teardown.

Dependencies/integration: Uses shared `setup`, `operations`, `client`, storage-control client support for hierarchical buckets, and testify. It depends on the package-level `testEnv` initialized by `setup_test.go`.

Risks/test signals: Error-string matching in the first test is path-format sensitive. The second test branches on bucket type, making HNS/flat behavior explicit. A passing run signals correct negative-cache TTL semantics and EEXIST behavior under out-of-band mutations.
