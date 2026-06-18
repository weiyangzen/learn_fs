# sources/user-network-fs/rclone/librclone/librclone.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/librclone.go -->
## sources/user-network-fs/rclone/librclone/librclone.go

Purpose: C-exported main package for building rclone as a shared or static library.

Important APIs and control flow: cgo declares `struct RcloneRPCResult { char* Output; int Status; }`. `RcloneInitialize` and `RcloneFinalize` delegate lifecycle to the internal library. `RcloneRPC(method, input)` converts C strings to Go strings, calls internal `librclone.RPC`, allocates the output as `C.CString`, and returns status/output in the C struct. `RcloneFreeString` frees strings returned by `RcloneRPC`. `main` is empty for library builds.

State, dependencies, and integration: blank imports register all backends, mount commands, operations/sync RC commands, and plugins. It depends on cgo and `unsafe` for C memory release. It is consumed by C, PHP FFI, Python ctypes, and other native integrations.

Risks and test signals: caller must free `Output`; failure to do so leaks C heap memory. All strings are expected UTF-8. Go panic handling is in internal `RPC`, not this wrapper. C demo and Python tests exercise this ABI.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/librclone.go -->
