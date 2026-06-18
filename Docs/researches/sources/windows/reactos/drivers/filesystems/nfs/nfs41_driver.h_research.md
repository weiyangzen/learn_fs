# File Research: sources/windows/reactos/drivers/filesystems/nfs/nfs41_driver.h

This header defines public names, IOCTLs, daemon opcodes, security flavors, and driver lifecycle states for the NFSv4.1 Windows/ReactOS mini-redirector.

It declares kernel and user-visible device names for the main driver (`\Device\nfs41_driver`, `\\.\nfs41_driver`), a pipe device (`\Device\nfs41_pipe`), provider display names (`NFS41 Network`), and shared-memory object names (`\BaseNamedObjects\nfs41_shared_memory`, `Global\nfs41_shared_memory`).

The `_RDR_CTL_CODE` macro creates network-redirector IOCTL codes. Defined IOCTLs are:
- `IOCTL_NFS41_START`
- `IOCTL_NFS41_STOP`
- `IOCTL_NFS41_GETSTATE`
- `IOCTL_NFS41_ADDCONN`
- `IOCTL_NFS41_DELCONN`
- `IOCTL_NFS41_READ`
- `IOCTL_NFS41_WRITE`
- `IOCTL_NFS41_INVALCACHE`

The `nfs41_opcodes` enum is the kernel/daemon request vocabulary used by `nfs41_driver.c`: mount, unmount, open, close, read, write, lock, unlock, directory query, file query/set, EA get/set, symlink, volume query, ACL query/set, shutdown, and an invalid sentinel.

`rpcsec_flavors` names supported authentication/security modes: AUTH_SYS and Kerberos `krb5`, `krb5i`, `krb5p`.

Two lifecycle enums track initialization and runtime start state. `nfs41_init_driver_state` distinguishes startable, start-in-progress, and started initialization. `nfs41_start_driver_state` distinguishes startable, start-in-progress, started, and stopped runtime states. These states are used by the device-control path to report/start/stop the mini-redirector.
