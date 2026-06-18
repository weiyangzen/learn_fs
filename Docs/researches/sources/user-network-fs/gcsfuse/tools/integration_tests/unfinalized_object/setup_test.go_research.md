# sources/user-network-fs/gcsfuse/tools/integration_tests/unfinalized_object/setup_test.go

## Purpose

Bootstraps integration tests for unfinalized and appendable zonal objects. It restricts the package to zonal bucket runs, builds fallback configs for read, operation, and tailing-read suites, and wires static mounting for each compatible flag set.

## Important APIs, control flow, and dependencies

`TestMain` loads `cfg.UnfinalizedObject`, supplies fallback config items for `TestUnfinalizedObjectReadTest`, `TestUnfinalizedObjectOperationTest`, and `TestUnfinalizedObjectTailingReadTest`, calls `setup.TestEnvironment`, exits early when `setup.IsZonalBucketRun` is false, creates a storage client, handles mounted-directory mode, sets up the test bucket directory, and stores `mountFunc` as `static_mounting.MountGcsfuseWithStaticMountingWithConfigFile`.

## State, persistence, dependencies, and integration points

The package globals mirror stale-handle setup: `testEnv`, `mountFunc`, `mountDir`, and `rootDir`. Fallback flags vary metadata cache TTL and `--enable-kernel-reader=false` because these tests depend on fresh or cached stat/read behavior after remote appends to an unfinalized object.

## Risks and test signals

Primary risks are accidentally running against non-zonal buckets, where appendable object semantics are unavailable, and stale metadata cache hiding size or generation changes. Signals are early skip for non-zonal environments, successful setup of zonal static or mounted-directory runs, and downstream read/operation/tailing tests observing unfinalized object behavior.
