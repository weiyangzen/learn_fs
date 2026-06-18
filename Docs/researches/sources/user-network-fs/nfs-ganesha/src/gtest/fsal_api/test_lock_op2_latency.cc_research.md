<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_lock_op2_latency.cc -->
## sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_lock_op2_latency.cc

Purpose: smoke-test and benchmark FSAL byte-range lock operation `lock_op2`.

Important APIs/types/functions: fixture creates a regular test file. Tests prepare `fsal_lock_param_t request_lock` and call `test_file->obj_ops->lock_op2(..., FSAL_OP_LOCK, ...)`; bypass tests operate on `mdcdb_get_sub_handle(test_file)`.

Control flow/state: simple tests perform one lock call. Loop tests perform one million lock calls and time them. Persistent state is the test file plus any lock state registered in the backend/state subsystem.

Dependencies/integration: requires backend `lock_op2` implementation and the Ganesha locking/state code. The test passes null owner/state-like arguments, so it mostly exercises minimal FSAL lock path handling.

Risks: repeatedly taking the same lock without explicit unlock may depend on backend idempotency or owner interpretation. Null lock owner/state arguments may not represent real NFS lock flow. Bypass mode avoids MDCACHE policy checks.

Test signals: zero major status for lock operations and printed average nanoseconds per `lock_op2` for normal and bypass paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/gtest/fsal_api/test_lock_op2_latency.cc -->
