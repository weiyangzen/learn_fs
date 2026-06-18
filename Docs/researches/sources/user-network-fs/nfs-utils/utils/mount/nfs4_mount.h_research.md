# sources/user-network-fs/nfs-utils/utils/mount/nfs4_mount.h

Purpose: defines the legacy userspace-to-kernel data structure for NFSv4 mounts and declares `nfs4mount()`.

Important APIs and types: `struct nfs_string` is a length/data pair. `struct nfs4_mount_data` contains versioned fields for flags, transfer/cache parameters, client address, mount path, hostname, server sockaddr, transport protocol, and auth flavor array. Flag constants include soft, intr, nocto, noac, strictlock, unshared, and mask.

Control flow and integration: `nfs4mount.c` fills this structure and passes it to `mount(2)` for filesystem type `nfs4` in legacy binary mount-data mode.

State and persistence: no state here; field order is a kernel ABI compatibility contract.

Dependencies: uses `struct sockaddr` and is included alongside networking headers.

Risks and tests: comments warn not to reorder fields; changing layout breaks kernel compatibility. Test signals include compile-time structure availability, version value, flag translation from options, and mount syscall data population.
