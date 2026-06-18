# sources/user-network-fs/gcsfuse/tools/integration_tests/streaming_writes/setup_test.go

## Purpose

Bootstraps the streaming-writes integration package. It loads configuration, supplies fallback streaming-write flags, creates the shared storage client, handles mounted-directory mode, and runs the package tests once for each compatible static mount flag set.

## Important APIs, control flow, and dependencies

`TestMain` uses `setup.ParseSetUpFlags`, `test_suite.ReadConfigFile`, `setup.TestEnvironment`, `client.CreateStorageClient`, `setup.RunTestsForMountedDirectory`, `setup.BuildFlagSets`, `setup.SetUpTestDirForTestBucket`, and `static_mounting.RunTestsWithConfigFile`. The fallback config uses `--rename-dir-limit=3`, one MiB write blocks, max two blocks per file, unlimited global blocks, and both HTTP and gRPC client protocol variants, compatible with flat, HNS, and zonal buckets.

## State, persistence, dependencies, and integration points

The package-global `testEnv` stores the config, context, storage client, and per-suite test directory. Static mounting is delegated to the mounting utility, which remounts per flag set and invokes the package's Go tests against the same storage client.

## Risks and test signals

Global setup risk includes missing config, stale mount directories, and cross-flag leakage if cleanup fails. The strongest signals are successful execution under all generated flag sets, log preservation on failure, and correct behavior in both mounted-directory and self-managed static mount modes.
