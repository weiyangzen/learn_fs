# File Research: sources/os/linux/linux/fs/nfs/sysctl.c

Registers the NFS client sysctl tunables under `fs/nfs`.

Key behavior:
- Defines sysctls for:
  - `nfs_mountpoint_timeout`, backed by `nfs_mountpoint_expiry_timeout` and handled as jiffies.
  - `nfs_congestion_kb`, backed by `nfs_congestion_kb`.
- `nfs_register_sysctl()` registers the table and returns `-ENOMEM` on failure.
- `nfs_unregister_sysctl()` unregisters the table and clears the saved header pointer.

Important interactions:
- Called from `register_nfs_fs()` and `unregister_nfs_fs()` in `super.c`.
- `nfs_congestion_kb` is initialized and consumed by `write.c` for client writeback congestion control.
