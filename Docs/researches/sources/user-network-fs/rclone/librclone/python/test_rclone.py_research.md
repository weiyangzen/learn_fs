# sources/user-network-fs/rclone/librclone/python/test_rclone.py

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/python/test_rclone.py -->
## sources/user-network-fs/rclone/librclone/python/test_rclone.py

Purpose: unittest coverage for the Python ctypes wrapper and shared library build path.

Important APIs and control flow: `setUpClass` builds `./librclone.so` if missing and initializes one shared `Rclone` instance. `tearDownClass` closes it and removes the shared object. `test_rpc` calls `rc/noop` and expects the same dict back. `test_rpc_error` calls `rc/error`, expects `RcloneException`, checks status 500, and checks the error prefix.

State, dependencies, and integration: depends on `go build`, local compiler support for `librclone`, and the Python wrapper. It mutates the current directory by creating/removing `librclone.so`.

Risks and test signals: this is an integration test, not a fast pure unit test. It does not cover memory-free behavior under JSON decode failures or finalizer edge cases.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/python/test_rclone.py -->
