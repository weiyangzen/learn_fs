<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/setup_test.go -->
# sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/setup_test.go

## Purpose

This package setup file configures and runs all local file integration tests. It defines default flag matrices for local-file write behavior and runs the same suite under static, only-dir, and dynamic mounting.

## Important APIs, Types, and Functions

`TestMain` sets `testDirName`, reads or builds `cfg.LocalFile`, creates the shared storage client/context, handles mounted-directory mode, builds flag sets, sets up the test bucket directory, and invokes `static_mounting.RunTestsWithConfigFile`, `only_dir_mounting.RunTestsWithConfigFile`, and `dynamic_mounting.RunTestsWithConfigFile`. It also defines `LocalFileTestSuite` and `TestLocalFileTestSuite`.

## Control Flow

Default configs include implicit-dirs true/false, rename-dir-limit, streaming writes disabled, grpc protocol, and write block/global block limits. After environment setup, mounted-directory runs are delegated. Otherwise static mounting runs first; only-dir mounting runs if static passes; dynamic mounting runs if only-dir passes.

## State and Persistence Behavior

The file owns package-level `ctx`, `storageClient`, `testDirName`, and mount mode state consumed by all local file tests. It does not itself clean GCS after dynamic mode in this snippet, relying on mounting utilities and per-test setup helpers.

## Dependencies and Integration Points

It integrates shared setup/test-suite config, static/dynamic/only-dir mounting utilities, and Testify suite execution. It is the root lifecycle for all `local_file` test files.

## Risks and Test Signals

Multiple mount modes in one process require globals to remain coherent. Flag compatibility excludes zonal for some global-block cases. Success is all suite methods passing across selected mount variants.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/tools/integration_tests/local_file/setup_test.go -->
