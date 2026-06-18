# sources/user-network-fs/rclone/cmd/mountlib/rc.go

Purpose: exposes mount lifecycle over rclone RC: create, unmount, list types, list mounts, and unmount all.

Important APIs/state: mutex `mountMu`, maps `mountFns` and `liveMounts`, `supportedMountTypes`, `ResolveMountMethod`, `AddRc`, RC handlers `mountRc`, `unMountRc`, `mountTypesRc`, `listMountsRc`, `unmountAll`, and JSON-facing `MountInfo`.

Control flow: mount backends register with `AddRc`. `mountRc` parses `fs`, `mountPoint`, optional mount/vfs options, rejects daemon mode, resolves backend, creates/mounts `MountPoint`, starts a goroutine to `Wait` and remove from `liveMounts`, then stores and returns actual mountpoint. Unmount handlers find live mounts under mutex and call `Unmount`.

State/persistence: maintains process-local live mount registry and OS mounts. Dependencies include `fs/rc` and VFS options. Risks include holding `mountMu` during potentially slow mount setup, unsynchronized captured `err` in wait goroutine, registry inconsistencies if unmount races with wait cleanup, and daemon unsupported over API. Tests cover registration, error cases, mount/list/unmount on capable systems.
