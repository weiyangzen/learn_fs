# sources/user-network-fs/gcsfuse/tools/integration_tests/util/mounting/dynamic_mounting/dynamic_mounting.go

Purpose: provides integration-test orchestration for dynamic bucket mounting, where the root mount exposes accessible buckets and tests run inside the selected test bucket subdirectory.

Important APIs/types/functions: `MountGcsfuseWithDynamicMountingWithConfig`, deprecated `MountGcsfuseWithDynamicMounting`, `runTestsOnGivenMountedTestBucket`, `executeTestsForDynamicMounting`, and `RunTestsWithConfigFile`.

Control flow: default log flags and the root mount directory are appended to each flag set, gcsfuse is mounted, the effective test mount path is changed to `<root>/<bucket>`, tests run, then global and config mount paths are restored before unmounting.

State/persistence behavior: mutates `setup` globals via `SetMntDir` and `SetDynamicBucketMounted`, and mutates `TestConfig.GCSFuseMountedDirectory` during each iteration. Persistent effects are the gcsfuse mount and log file.

Dependencies/integration: wraps `mounting.MountGcsfuse`, `setup.ExecuteTest`, `setup.UnMountAndThrowErrorInFailure`, and the common `test_suite.TestConfig`.

Risks/test signals: failures can leave global mount state inconsistent if cleanup paths are interrupted. The deprecated signature ignores its `context` and storage client parameters, signaling ongoing migration to config-file driven tests.
