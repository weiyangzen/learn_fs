# sources/user-network-fs/rclone/librclone/python/rclone.py

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/python/rclone.py -->
## sources/user-network-fs/rclone/librclone/python/rclone.py

Purpose: Python ctypes wrapper around the C `librclone` shared library.

Important APIs and control flow: `RcloneRPCString` subclasses `c_char_p` so ctypes preserves the raw pointer for `RcloneFreeString`. `RcloneRPCResult` mirrors the C struct. `RcloneException` carries decoded error output and status. `Rclone.__init__` loads the shared library, configures function restypes/argtypes, and initializes rclone. `rpc(method, **kwargs)` JSON-encodes kwargs, calls `RcloneRPC`, decodes JSON output, frees the C string, raises `RcloneException` on non-200 status, and returns the decoded dict. `close` finalizes and clears the handle. `build` compiles the shared library if missing.

State, dependencies, and integration: depends on `ctypes`, `json`, `os`, `subprocess`, and the Go toolchain for `build`. It integrates with Python applications needing local RC calls without an HTTP server.

Risks and test signals: `rpc` assumes output is valid JSON and frees after decode; if decode raises before free, the current code may leak the C string. `close` is manual and repeated calls after close would fail. The Python test covers success and RC error conversion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/python/rclone.py -->
