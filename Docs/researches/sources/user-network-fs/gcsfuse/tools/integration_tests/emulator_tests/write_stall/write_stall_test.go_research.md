# Research: sources/user-network-fs/gcsfuse/tools/integration_tests/emulator_tests/write_stall/write_stall_test.go

Purpose: package setup for write-stall emulator tests. It declares shared mount directory state and configures static mounting against the emulator bucket.
Important APIs and state: globals `testDirPath`, `mountFunc`, and `rootDir`; `TestMain` parses setup flags, skips mounted-directory mode, prepares the test bucket flag, sets `rootDir`, and assigns static mounting.
Control flow: normal mode runs tests after static mount function setup; tests themselves mount per scenario with proxy endpoints and unmount using `rootDir`.
State and persistence: this file stores only package-global mount/test path state. Per-test file data and proxy process state are handled in `writes_stall_on_sync_test.go`.
Dependencies and integration points: depends on `setup` and `static_mounting`, and on `emulator_tests.sh` for emulator env vars and bucket creation.
Risks and edge cases: no dynamic/only-dir coverage; mounted-directory mode simply logs and returns. Fixed root dir is shared across tests but each test mounts/unmounts serially in package execution.
Test signals: successful setup means write-stall scenarios can call `setup.MountGCSFuseWithGivenMountFunc` and unmount cleanly.
