# File Research: sources/os/linux/linux/fs/nfs/nfs4sysctl.c

## Purpose

`nfs4sysctl.c` registers the NFSv4 client sysctl controls under `fs/nfs`. It exposes runtime-tunable values for callback service port selection and idmapper cache timeout.

## Sysctl Table

`nfs4_cb_sysctls` defines two entries:

- `nfs_callback_tcpport`
  - Backs onto `nfs_callback_set_tcpport`.
  - Uses `proc_dointvec_minmax`.
  - Accepts integer values from `0` through `65535`.
  - Mode `0644`, so root can update and users can read according to procfs permissions.
- `idmap_cache_timeout`
  - Backs onto `nfs_idmap_cache_timeout`.
  - Uses `proc_dointvec`.
  - Mode `0644`.

The bounds for callback TCP port are represented by `nfs_set_port_min` and `nfs_set_port_max`.

## Public Entry Points

- `nfs4_register_sysctl()` calls `register_sysctl("fs/nfs", nfs4_cb_sysctls)` and stores the returned `ctl_table_header`. It returns `-ENOMEM` when registration fails.
- `nfs4_unregister_sysctl()` unregisters the stored table header and clears the global pointer.

## Cross-File Relationships

- `nfs_callback_set_tcpport` comes from NFS callback support.
- `nfs_idmap_cache_timeout` comes from NFSv4 idmapping.
- `nfs4super.c` calls registration during NFSv4 module initialization and unregisters during module exit.

## Research Notes

The file is intentionally narrow: it does not implement the callback service or idmapper cache behavior. It only exposes the knobs and binds validation/permission policy for procfs sysctl access.
