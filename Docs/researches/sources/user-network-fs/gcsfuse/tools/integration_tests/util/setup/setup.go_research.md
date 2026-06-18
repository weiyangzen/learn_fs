# sources/user-network-fs/gcsfuse/tools/integration_tests/util/setup/setup.go

Purpose: central integration-test setup package for flags, global test state, gcsfuse build/install selection, mount directories, log artifacts, bucket type detection, config-derived flag sets, and mount/unmount helpers.

Important APIs/types/functions: flag accessors, global setters/getters, `SetUpTestDir`, `UnMount`, `ExecuteTestForFlagsSet`, skip helpers, `SetUpTestDirForTestBucket`, `SetupTestDirectory`, `CleanupDirectoryOnGCS`, `BucketType`, `BuildFlagSets`, `SetGlobalVars`, `GetBucketAndObjectBasedOnTypeOfMount`, mount wrappers, proxy-log helpers, GCE zone/region helpers, profiler flag parsers, and log-file path setup.

Control flow: tests parse flags, choose installed/prebuilt/source-built gcsfuse, create temp mount/log paths, derive bucket type through the storage API, build compatible flag sets from YAML config, mount if needed, execute tests, unmount, and save logs on failure.

State/persistence behavior: package-level globals hold binary paths, log path, mount dir, test dir, bucket, only-dir/dynamic mount context, billing project, and key file. It creates temp directories, writes artifact logs, deletes local directories, and deletes GCS objects during cleanup.

Dependencies/integration: integrates with Google Cloud Storage clients, experimental gRPC bidi reads, auth credentials, OpenTelemetry GCP resource detection, internal build utility, `test_suite` config models, and system `fusermount`.

Risks/test signals: global mutable state makes tests order-sensitive and migration-sensitive. Several helpers call `os.Exit` or `log.Fatal`, so failures can bypass defers. Bucket cleanup splits bucket/path with a simple two-element assumption.
