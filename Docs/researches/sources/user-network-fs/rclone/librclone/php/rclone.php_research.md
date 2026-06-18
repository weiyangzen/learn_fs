# sources/user-network-fs/rclone/librclone/php/rclone.php

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/php/rclone.php -->
## sources/user-network-fs/rclone/librclone/php/rclone.php

Purpose: PHP FFI wrapper around `librclone.so`.

Important APIs and control flow: class `Rclone` loads C definitions for `RcloneRPCResult`, lifecycle functions, `RcloneRPC`, and `RcloneFreeString` from a supplied shared library path. The constructor calls `RcloneInitialize`. `rpc($method, $input)` invokes `RcloneRPC`, copies the C string to a PHP string, stores status, frees the C output string, and returns an array with `output` and `status`. `close()` calls `RcloneFinalize`.

State, dependencies, and integration: object state is the FFI handle and latest output struct. It depends on PHP FFI and the C shared library ABI.

Risks and test signals: callers must pass JSON strings, not PHP arrays. `close` is manual; there is no destructor safety net. The wrapper does not throw on non-200 status. The companion PHP test demonstrates remote operations but depends on configured remotes.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/php/rclone.php -->
