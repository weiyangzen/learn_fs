# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfsid.h

This header defines the user/group id-to-name mapping ABI used by NFSv4 owner and owner_group handling.

Key behavior:
- Defines `struct nfsd_idargs`, the argument block for id/name updates from userland, including flag, uid, gid, cache maximum, timeout, name pointer/length, group list pointer, and group count.
- Defines operation flags for initializing the mapping domain, adding/deleting uid mappings, adding/deleting username mappings, adding/deleting gid mappings, adding/deleting group-name mappings, and marking the name pointer as kernel-space.
- Under kernel builds, defines `struct nfs_prime_userd`, the minimal bootstrap mapping record used before `nfsuserd(8)` is available.
- Declares `nfssvc_idname()` for kernel consumers.

Important interactions:
- `nfs_commonsubs.c` implements `nfssvc_idname()` and consumes the flag definitions to update per-vnet user/group hash caches.
- The structure forms part of the `nfssvc(2)` path used by userland `nfsuserd`.
- Bootstrap mappings must match system passwd/group identities for root/bin/wheel/operator/nobody-style entries.

Edge cases:
- `NFSID_SYSSPACE` controls whether names are copied from user memory or kernel memory.
- Group lists are only meaningful for uid mappings that also populate a credential with server-side group membership.
