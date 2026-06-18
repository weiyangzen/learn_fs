<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_mkdir_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_mkdir_latency.cc

Purpose: benchmarks directory creation via `mkdir` object op and `fsal_create(..., DIRECTORY, ...)`.

Important APIs/types/functions: tests use `obj_ops->mkdir`, `fsal_create`, `lookup`, `unlink`, `fsal_remove`, `mdcdb_get_sub_handle`, and `gtws_subcall` to switch `op_ctx->fsal_export` for backend subcalls. Full fixture pre-populates 100000 files.

Control flow/state: simple tests create one directory, verify lookup returns the created handle, then remove it. Loop tests create one million generated directories and remove them. Full tests repeat in a populated directory, with bypass variants calling backend FSAL directly and using backend unlink cleanup.

Dependencies/integration: writable export with directory creation, MDCACHE internals for bypass, and the embedded Ganesha harness.

Risks: `gtws_subcall` temporarily mutates global/thread operation context and must always restore it. Million-directory loops are expensive and can stress backend directory scaling. The test name `TEST_ROOT` is also used as a child directory name inside the test root, which can be confusing.

Test signals: zero major status, lookup identity checks, cleanup removes all generated directories, and average timings for object-op, wrapper, populated-directory, and bypass mkdir paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_mkdir_latency.cc -->
