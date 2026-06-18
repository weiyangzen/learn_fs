# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/grpc_header_validation/setup_test.go

Purpose: package-level setup for emulator gRPC header validation tests. It prepares a static mounting function and root mount directory for tests that run only against the emulator-created test bucket.
Important APIs and state: globals `mountFunc` and `rootDir`; `TestMain` parses setup flags, rejects mounted-directory mode, calls `setup.SetUpTestDirForTestBucketFlag`, sets `rootDir = setup.MntDir()`, and selects `static_mounting.MountGcsfuseWithStaticMounting`.
Control flow: if `--mountedDirectory` is set, the package logs and returns without running tests. Otherwise it prepares test-dir state and executes the package tests.
State and persistence: no storage client is created here; state is limited to mount root and setup flags. Actual file/object state is managed in test methods through mounted paths and emulator config.
Dependencies and integration points: consumed by `grpc_header_validation_test.go`, which calls `setup.MountGCSFuseWithGivenMountFunc(g.flags, mountFunc)` and unmounts `rootDir`.
Risks and edge cases: returning from `TestMain` instead of `os.Exit(0)` for mounted-directory mode may be surprising but effectively skips. Fixed static mounting means dynamic/only-dir modes are not covered.
Test signals: successful setup lets tests start proxy and mount using the configured static mount function.
