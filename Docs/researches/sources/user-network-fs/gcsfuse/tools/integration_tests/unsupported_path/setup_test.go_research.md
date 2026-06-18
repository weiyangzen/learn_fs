# sources/user-network-fs/gcsfuse/tools/integration_tests/unsupported_path/setup_test.go

## Purpose

Bootstraps integration tests for GCS object names that cannot be represented cleanly as POSIX paths. It loads or supplies config with unsupported-path support enabled and runs the package over compatible static mount flag sets or a provided mounted directory.

## Important APIs, control flow, and dependencies

`TestMain` defines `DirForUnsupportedPathTests`, parses setup flags, reads `cfg.UnsupportedPath`, supplies fallback flags with `--implicit-dirs`, `--enable-unsupported-path-support=true`, high rename-dir limit, negative metadata cache disabled, and gRPC/non-gRPC variants. It initializes `ctx`, `bucketType`, `storageClient`, builds flag sets, sets up the test directory, and calls `static_mounting.RunTestsWithConfigFile`.

## State, persistence, dependencies, and integration points

The globals `storageClient`, `ctx`, and `bucketType` are consumed by the test suite. Bucket-type knowledge matters because zonal tests create finalized objects while flat/HNS use normal object creation.

## Risks and test signals

Risks include unsupported-path support not actually enabled, incompatible gRPC zonal coverage, and globals being unset if setup exits early. Signals are successful mount initialization and downstream tests observing unsupported object filtering, copying, rename, and deletion behavior.
