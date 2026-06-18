# sources/user-network-fs/rclone/cmd/mountlib/mount.go

Purpose: shared mount command/lifecycle library for FUSE-like backends (`mount`, `cmount`, `mount2`, `nfsmount`). It defines options, command construction, daemon handling, VFS setup, wait, and unmount lifecycle.

Important APIs/types: embedded `mountHelp`, `OptionsInfo`, `Options`, `MountFn`, `UnmountFn`, `MountPoint`, `NewMountPoint`, global `Opt`, `AddFlags`, `WaitMountReady`, `NewMountCommand`, and `MountPoint` methods `Mount`, `Wait`, `Unmount`.

Control flow: `NewMountCommand` validates args, adjusts daemon config, sets fallback PATH, optionally starts stats, builds `MountPoint`, calls `Mount`, then either waits in foreground or waits for daemon readiness. `Mount` defaults volume/device names, optionally daemonizes, builds `vfs.New`, calls backend `MountFn`, and records actual mountpoint/time. `Wait` listens for backend errors and finalizes unmount through `atexit`.

State/persistence: creates live VFS state and OS mounts; daemon mode forks process; global `Opt` is flag-backed. Dependencies include config, daemonize, systemd, atexit, vfs flags. Risks include nil mount functions on unsupported builds, daemon readiness platform differences, cleanup on externally unmounted paths, and global option mutation.
