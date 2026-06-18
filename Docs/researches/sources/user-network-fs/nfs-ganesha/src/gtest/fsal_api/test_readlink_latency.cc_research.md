# sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_readlink_latency.cc

## Purpose
This test benchmarks FSAL symbolic-link target reads. It creates a symlink under the export root that points at the per-test root name, records its expected link content, and repeatedly invokes `readlink` through object operations, `fsal_readlink`, and MDCACHE bypass sub-handles.

## Important APIs, Types, And Functions
`ReadlinkEmptyLatencyTest` uses `fsal_create(..., SYMBOLIC_LINK, ..., TEST_ROOT, ...)`, `fsal_readlink`, `obj_ops->readlink`, `obj_ops->unlink`, and `gsh_free` for returned `utf8string` storage. `ReadlinkFullLatencyTest` primes the test root with `FILE_COUNT` regular files to measure readlink in a loaded cache/export.

## Control Flow, State, And Persistence
Setup creates `symlink_to_readlink_latency`, reads and stores its target into `bfr_content`, and releases create attributes. Simple tests read the link once and compare byte content with the stored target. Loop tests allocate a new returned target string on each iteration and free it immediately. Teardown frees the stored target string, unlinks the symlink from `root_entry`, releases the symlink handle, and delegates root cleanup to the base fixture.

## Dependencies And Integration Points
The test uses FSAL symlink creation and readlink semantics, MDCACHE sub-handle access, Ganesha memory allocation ownership for returned strings, and the shared Ganesha environment. `main` supports LTTng and profiling arguments but only configures the environment; no explicit profiling calls are used in the tests.

## Risks And Test Signals
The primary risk is allocation churn from one million `readlink` calls, each requiring `gsh_free` of returned content. `BIG_BYPASS` does not assert that `mdcdb_get_sub_handle` returned non-null before use. Correctness checks compare target contents in simple paths; loop paths assert only success and timing.
