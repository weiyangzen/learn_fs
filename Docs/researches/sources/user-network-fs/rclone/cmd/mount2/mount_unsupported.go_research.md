# sources/user-network-fs/rclone/cmd/mount2/mount_unsupported.go

Purpose: build-tag stub for platforms where go-fuse mount2 is unsupported (`!linux && !(darwin && amd64)`).

Important behavior: registers hidden `mount2` command with nil mount function through `mountlib.NewMountCommand`.

Control flow/state: no real mount implementation or persistence. It keeps command registration/doc shape consistent while preventing backend use on unsupported platforms.

Dependencies/integration: mountlib command registration. Risks include nil mount function user errors if command is invoked through hidden or RC paths. Coverage comes from build matrix.
