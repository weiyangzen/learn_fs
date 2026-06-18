# sources/user-network-fs/rclone/cmd/nfsmount/nfsmount.go

Purpose: Unix-only experimental mount backend that exposes the VFS through rclone’s NFS server and then invokes the system NFS mount command.

Important APIs/state: package globals `sudo` and `mountPath`; init registers `nfsmount` via mountlib and RC, adds `--sudo`, `--nfs-mount-path`, and NFS server flags. `mount` starts `nfs.NewServer`, discovers its random port, invokes `mount`, and returns unmount/async error handles.

Control flow: after NFS server starts, it builds mount options for `port`, `mountport`, `tcp`, extra `-o` options/flags, optionally prefixes `sudo`, and mounts `localhost:<mountPath>` to the mountpoint. Unmount uses `diskutil umount force` on Darwin or `umount -f`, then shuts down NFS server and VFS. `nfs.OnUnmountFunc` marks external unmount and completes async errors.

State/persistence: creates an NFS server, OS NFS mount, and VFS state. Dependencies include system `mount/umount/sudo`, `serve/nfs`, mountlib. Risks include command availability/permissions, global `nfs.OnUnmountFunc`, global `mountPath`, formatting bug using `%e` for errors, and cleanup ordering.
