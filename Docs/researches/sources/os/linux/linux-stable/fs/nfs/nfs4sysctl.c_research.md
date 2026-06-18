# File Research: sources/os/linux/linux-stable/fs/nfs/nfs4sysctl.c

## Purpose

`nfs4sysctl.c` provides the sysctl interface for a small set of NFSv4 client parameters under `/proc/sys/fs/nfs`.

## Sysctl Entries

The file defines `nfs4_cb_sysctls` with two entries:

- `nfs_callback_tcpport`
  - data: `nfs_callback_set_tcpport`
  - type/size: `int`
  - mode: `0644`
  - handler: `proc_dointvec_minmax`
  - range: `0` to `65535`

- `idmap_cache_timeout`
  - data: `nfs_idmap_cache_timeout`
  - type/size: `int`
  - mode: `0644`
  - handler: `proc_dointvec`

`nfs_set_port_min` is a static zero-initialized const int. `nfs_set_port_max` is `65535`.

## Registration Lifecycle

`nfs4_register_sysctl()` calls:

```c
register_sysctl("fs/nfs", nfs4_cb_sysctls)
```

It stores the returned table header in `nfs4_callback_sysctl_table` and returns `-ENOMEM` if registration fails.

`nfs4_unregister_sysctl()` unregisters the table and clears the global pointer.

## Cross-File Relationships

`nfs4super.c` calls:
- `nfs4_register_sysctl()` during NFSv4 module init.
- `nfs4_unregister_sysctl()` during module exit.

`nfs4state.c` reads callback TCP port state indirectly during clientid setup when it chooses callback ports from the NFS network namespace.

## Research Takeaways

This file is intentionally small and has no complex state machine. It exposes callback TCP port configuration and idmapper cache timeout through sysctl, with lifecycle owned by the NFSv4 module init/exit path.
