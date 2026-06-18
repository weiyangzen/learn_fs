<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_handle_to_key_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_handle_to_key_latency.cc

Purpose: benchmarks FSAL handle-to-key conversion.

Important APIs/types/functions: fixture creates a regular test file using `fsal_create` and removes it in teardown. Tests call `test_file->obj_ops->handle_to_key` or the same operation on `mdcdb_get_sub_handle(test_file)`, using `gsh_buffdesc` for returned key address/length.

Control flow/state: `SIMPLE` and `SIMPLE_BYPASS` validate that conversion produces a non-null address and non-zero length. `LOOP` and `LOOP_BYPASS` reset `fh_desc` and time one million conversions. Persistent state is the one test file.

Dependencies/integration: requires FSAL handle implementation and MDCACHE debug access for bypass. The test harness parses standard config/export/tracing/profiling flags.

Risks: the returned `gsh_buffdesc.addr` ownership is not released in loops, which is safe only if `handle_to_key` points into stable handle memory rather than allocating each call. Backend implementations with allocation semantics would leak under the benchmark.

Test signals: non-null/non-zero handle key assertions and average nanoseconds per `handle_to_key` printed for cached and bypass paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_handle_to_key_latency.cc -->
