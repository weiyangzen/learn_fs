# File Research: sources/os/linux/linux-stable/fs/nfs/sysctl.c

Purpose: Registers global NFS client sysctl tunables under `fs/nfs`.

Key responsibilities:
- Exposes `nfs_mountpoint_timeout` backed by `nfs_mountpoint_expiry_timeout` using jiffies conversion.
- Exposes `nfs_congestion_kb` backed by the writeback congestion threshold.
- Provides `nfs_register_sysctl` and `nfs_unregister_sysctl`.

Integration:
- Called from `register_nfs_fs` / `unregister_nfs_fs` in `super.c`.
- `nfs_congestion_kb` is consumed by `write.c`.

Risks and notes:
- Registration failure propagates as `-ENOMEM`.
