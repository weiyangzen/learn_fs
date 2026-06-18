# sources/user-network-fs/rclone/lib/sdactivation/sdactivation_stub.go

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/lib/sdactivation/sdactivation_stub.go -->
## sources/user-network-fs/rclone/lib/sdactivation/sdactivation_stub.go

Purpose: provides systemd socket activation stubs on Windows and Plan 9, where the upstream go-systemd activation package is not buildable or useful.

Important APIs and control flow: `ListenersWithNames()` returns an empty map and nil error. `Listeners()` returns nil slice and nil error. Both match the real package API without doing work.

State, dependencies, and integration: there is no state. It depends only on `net` for type signatures. It allows cross-platform imports of `lib/sdactivation` without conditional caller code.

Risks and test signals: callers cannot distinguish unsupported platform from "no activated sockets" except through build target knowledge. No tests are included in the requested set.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/lib/sdactivation/sdactivation_stub.go -->
