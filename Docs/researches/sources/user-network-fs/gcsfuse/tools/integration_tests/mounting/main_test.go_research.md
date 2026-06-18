<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/main_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/main_test.go

## Purpose

This package setup file initializes the canned mounting integration tests. It parses flags, finds fusermount, reads config, skips mounted-directory runs, and builds or locates the gcsfuse binaries used by `gcsfuse_test.go` and `mount_helper_test.go`.

## Important APIs, Types, and Functions

Globals `gBuildDir` and `gFusermountPath` are shared by the package. `TestMain` uses `setup.ParseSetUpFlags`, `test_suite.ReadConfigFile`, `exec.LookPath`, `setup.TestInstalledPackage`, and `util.BuildGcsfuse`.

## Control Flow

After parsing flags, Linux runs locate `fusermount`. If no `Mounting` config exists, one is synthesized from test bucket and mounted directory flags. Mounted-directory mode exits early because these tests build/mount their own canned bucket. Installed-package mode sets `gBuildDir="/"` and runs tests. Otherwise a temp build directory is created, gcsfuse is built into it, tests run, the directory is removed, and the process exits with the test code.

## State and Persistence Behavior

State includes a temporary build directory containing `bin/gcsfuse` and `sbin/mount.*` helpers, plus the fusermount path. The directory is removed after tests unless installed-package mode is used.

## Dependencies and Integration Points

It is the lifecycle root for the mounting package and provides globals consumed by the command and mount-helper suites. It integrates setup/test-suite config with local binary build utilities.

## Risks and Test Signals

Build failures or missing fusermount abort the package. Installed-package mode assumes helper/binary paths under `/`. Success is a usable binary/helper layout for downstream mounting tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/mounting/main_test.go -->
