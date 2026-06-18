# sources/user-network-fs/gcsfuse/tools/integration_tests/stale_handle/setup_test.go

## Purpose

Bootstraps the stale file handle integration package. It loads the stale-handle test configuration, supplies fallback flag sets for streaming-writes enabled and disabled modes, creates the shared GCS storage client, decides whether the package is running against an already mounted directory or a statically mounted test bucket, and wires the package-global mount function and mount paths used by the suites.

## Important APIs, control flow, and dependencies

`TestMain` calls `setup.ParseSetUpFlags`, `test_suite.ReadConfigFile`, `setup.TestEnvironment`, `client.CreateStorageClient`, `setup.RunTestsForMountedDirectory`, `setup.SetUpTestDirForTestBucket`, and `static_mounting.MountGcsfuseWithStaticMountingWithConfigFile`. The fallback configuration creates two `ConfigItem`s keyed by `Run`: `TestStaleHandleStreamingWritesEnabled` uses zero metadata TTL plus one MiB write blocks, and `TestStaleHandleStreamingWritesDisabled` forces `--enable-streaming-writes=false`; each includes HTTP and gRPC flag variants and compatibility for flat, HNS, and zonal buckets.

## State, persistence, dependencies, and integration points

The package-global `testEnv` stores `context.Context`, `*storage.Client`, selected `*test_suite.TestConfig`, bucket type, and the current test directory. `mountDir`, `rootDir`, and `mountFunc` are shared with the stale-handle suites. Mounted-directory mode is intentionally restricted to cases where both mounted directory and bucket are known, because tests validate remote bucket contents as well as local file-handle behavior.

## Risks and test signals

Risk is concentrated in global setup: an absent config causes mounted-directory tests to exit early, stale globals affect all suites in the package, and a mismatch between bucket type and flags can hide stale-handle regressions. The main test signal is successful package initialization across dynamic config, fallback flags, GKE mounted directory mode, and static mount mode with the storage client closed after `m.Run`.
