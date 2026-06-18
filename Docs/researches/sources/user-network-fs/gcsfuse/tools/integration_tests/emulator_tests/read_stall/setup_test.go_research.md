# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/read_stall/setup_test.go

Purpose: package setup for read-stall emulator tests. It defines shared mount/test directory variables and chooses static mounting against the emulator test bucket.
Important APIs and state: globals `testDirPath`, `mountFunc`, and `rootDir`; `TestMain` parses setup flags, skips mounted-directory mode, sets up the test bucket flag, records `rootDir`, and assigns `static_mounting.MountGcsfuseWithStaticMounting`.
Control flow: mounted-directory mode logs and returns. Normal mode initializes test directory support, runs all tests, and exits with their status.
State and persistence: state is process-global and consumed by `read_stall_test.go`; test-created files persist only for the lifetime of the emulator bucket.
Dependencies and integration points: integrates with `emulator_tests.sh` environment variables and `setup.SetUpTestDirForTestBucketFlag`.
Risks and edge cases: static-only coverage misses dynamic mount behavior. The package assumes the parent script created `test-bucket`.
Test signals: setup succeeds when tests can mount using a proxy endpoint and unmount `rootDir` during teardown.
