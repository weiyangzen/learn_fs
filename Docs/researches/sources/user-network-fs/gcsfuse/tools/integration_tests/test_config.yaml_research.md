# sources/user-network-fs/gcsfuse/tools/integration_tests/test_config.yaml

## Purpose

Central YAML manifest for gcsfuse integration test suites. It maps suite names to mounted-directory placeholders, bucket placeholders, optional only-dir or secondary mount placeholders, flag matrices, bucket-type compatibility, optional `run` filters, and whether the case runs on GKE.

## Important APIs, control flow, and dependencies

The file is consumed by `test_suite.ReadConfigFile` and `setup.BuildFlagSets`. Top-level suites include directory behavior, operations, streaming writes, stale handles, unfinalized objects, unsupported paths, symlink handling, buffered/read cache, credential and mounting tests, flag optimizations, monitoring, managed folders, rapid appends, and concurrent operations. Relevant entries for this subset include `streaming_writes` flags with one MiB write blocks and unlimited global blocks, `stale_handle` split by streaming enabled/disabled `Run` names, `unfinalized_object` split by read/operation/tailing read runs and metadata TTLs, `unsupported_path` with `--enable-unsupported-path-support`, and `symlink_handling` split by standard-symlink enablement.

## State, persistence, dependencies, and integration points

The YAML is not executable but it controls runtime coverage and mount persistence behavior. Placeholder expansion injects bucket names, mounted directories, key files, billing projects, log files, cache paths, and profiler labels. Compatibility maps determine whether flat, HNS, or zonal buckets execute each flag set, and `run` names allow a package `TestMain` to run only the intended suite method.

## Risks and test signals

Risks include config drift from fallback configs embedded in Go files, comma-versus-space flag syntax differences, missing compatibility coverage, and stale `run` names silently skipping tests. Test signals are indirect: package `TestMain` functions should build non-empty compatible flag sets, run only matching suites when `run` is set, and skip incompatible bucket types as declared.
