# sources/user-network-fs/rclone/cmd/mount/mount_unsupported.go

Purpose: build-tag stub for unsupported platforms (`!linux`) for the bazil mount package.

Important behavior: imports only `mountlib` and registers `mountlib.NewMountCommand("mount", false, nil)` during init.

Control flow/state: no actual mount function exists; the command is still present but will fail through shared mountlib behavior if invoked. No persistence.

Dependencies/integration: keeps command registration consistent across platforms. Risks are user-facing error clarity when the mount function is nil. Test coverage is platform/build-matrix dependent.
