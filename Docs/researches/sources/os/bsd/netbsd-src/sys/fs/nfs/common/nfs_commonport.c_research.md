# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_commonport.c

This is the BSD/NetBSD port glue for the shared NFS implementation imported from FreeBSD-style `newnfs`. It owns global common-module storage, malloc types, mutexes, sysctls, module lifecycle, and small OS adaptation helpers.

Key contents:
- Defines common globals such as `nfsv4root_mnt`, `nfsstatsv1`, `newnfs_numnfsd`, `nfs_numnfscbd`, `nfsv4_callbackaddr`, `newnfsd_callout`, and function-pointer hooks used by client/server modules.
- Registers `vfs.nfs` sysctls for realignment counters, callback address, debug level, and uid/name hash size.
- Defines all `M_NEWNFS*` malloc buckets used by common, client, server, session, state, and layout structures.
- Implements `newnfs_realign()` for strict-alignment architectures by rebuilding unaligned mbuf chains into aligned mbufs.
- Provides small portability wrappers: `nfsrv_lookupfilename()`, `newnfs_copycred()`, `nfsmsleep()`, `nfsvno_getfs()`, `nfsvno_pathconf()`, `newnfs_setroot()`, `newnfs_getcred()`, `nfs_catnap()`, and `nfs_supportsnfsv4acls()`.
- Implements common `nfssvc` handling for id/name cache updates, stats retrieval/zeroing, and `nfsuserd` port registration.
- `nfscommon_modevent()` initializes locks, callouts, common data, and the `nfsd_call_nfscommon` dispatch hook; unload refuses while nfsd, nfsuserd, or callback daemons are active.

Important dependencies:
- Relies on `nfs_commonsubs.c` for `newnfs_init()`, stats, id/name cache cleanup, and NFSv4 helper functions.
- Hooks into `nfs_nfssvc.c` through `nfsd_call_nfscommon`.
- Uses vnode/pathconf and ACL VOPs to adapt NFS protocol semantics to the local filesystem.

Risks and notes:
- The legacy stats compatibility copy is manual and easy to desynchronize if `nfsstatsv1` changes.
- Unload ordering is important because this file destroys shared mutexes used across client/server code.
