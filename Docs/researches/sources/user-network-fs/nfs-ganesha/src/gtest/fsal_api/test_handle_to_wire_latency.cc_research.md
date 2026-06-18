<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_handle_to_wire_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_handle_to_wire_latency.cc

Purpose: benchmarks converting FSAL object handles to wire-format NFSv4 digests.

Important APIs/types/functions: fixture creates/removes a regular test file. Tests call `obj_ops->handle_to_wire` with `FSAL_DIGEST_NFSV4` and `gsh_buffdesc`; bypass tests use `mdcdb_get_sub_handle(test_file)`.

Control flow/state: simple tests allocate a wire buffer through the operation, verify status, and free `fh_desc.addr`. Loop tests call conversion one million times and free the last buffer after timing. Persistent state is only the test file.

Dependencies/integration: FSAL must implement NFSv4 wire handle conversion. The benchmark integrates with MDCACHE bypass internals and the embedded Ganesha harness.

Risks: if `handle_to_wire` allocates a fresh buffer each call, loop tests free only the final pointer and leak prior allocations. If it reuses a buffer, freeing behavior must match ownership contract. The benchmark focuses latency and does not validate digest contents.

Test signals: zero major status from `handle_to_wire` and average timing output for direct and bypass conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_handle_to_wire_latency.cc -->
