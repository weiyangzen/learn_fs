# sources/user-network-fs/rclone/librclone/ctest/ctest.c

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/ctest/ctest.c -->
## sources/user-network-fs/rclone/librclone/ctest/ctest.c

Purpose: simple C test/demo for calling rclone's exported C API.

Important APIs and control flow: `testRPC` calls `RcloneRPC`, prints status/output, and frees output with `RcloneFreeString`. `testNoOp` calls `rc/noop` with nested JSON and asserts exact pretty-printed output and status 200. `testError` calls `rc/error` and asserts exact JSON error output and status 500. `testCopyFile` and `testListRemotes` demonstrate other RPCs but are commented out in `main`. `main` initializes librclone, runs no-op and error tests, finalizes, and exits success if assertions pass.

State, dependencies, and integration: depends on generated `librclone.h`, libc, and the exported Go functions. It validates C-side memory ownership by freeing every RPC output.

Risks and test signals: exact JSON formatting makes the test sensitive to rclone RC formatting changes. Some demo functions assume `/tmp` or configured remotes and are intentionally disabled. The active tests provide a good C ABI smoke test for success/error calls and memory release.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/ctest/ctest.c -->
