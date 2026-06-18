# sources/user-network-fs/rclone/cmd/nfsmount/nfsmount_unsupported.go

Purpose: non-Unix stub for `nfsmount`.

Important behavior: init registers `nfsmount` with mountlib using a nil mount function and annotates it as introduced in v1.65.

Control flow/state: no NFS server or mount implementation. It preserves command registration shape on unsupported platforms while causing runtime failure through shared mountlib if invoked.

Dependencies/integration: mountlib. Risks include user confusion if the command appears but cannot run. Build-matrix coverage only.
