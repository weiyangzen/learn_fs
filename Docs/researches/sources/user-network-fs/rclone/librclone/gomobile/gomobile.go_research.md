# sources/user-network-fs/rclone/librclone/gomobile/gomobile.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/gomobile/gomobile.go -->
## sources/user-network-fs/rclone/librclone/gomobile/gomobile.go

Purpose: exposes librclone shims with signatures acceptable to gomobile/gobind.

Important APIs and control flow: `RcloneInitialize` and `RcloneFinalize` delegate to internal `librclone.Initialize` and `Finalize`. `RcloneRPCResult` carries `Output string` and `Status int`. `RcloneRPC(method, input)` calls `librclone.RPC` and returns a pointer to a result struct.

State, dependencies, and integration: imports all backends and plugins by blank import, plus a mobile key-event package to keep go.mod dependency. It integrates with mobile bindings that cannot use the cgo exported ABI.

Risks and test signals: lifecycle semantics mirror internal librclone; repeated initialize/finalize is not strongly managed. RPC methods needing raw request/response are unsupported by the internal layer. No gomobile tests are present in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/librclone/gomobile/gomobile.go -->
