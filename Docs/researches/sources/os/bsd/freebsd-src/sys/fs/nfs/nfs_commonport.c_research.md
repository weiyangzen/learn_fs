# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_commonport.c

## Purpose

`nfs_commonport.c` is the FreeBSD-specific common port layer for the shared NFS implementation. It owns global storage, malloc types, mutex initialization, mbuf realignment for strict-alignment architectures, pathname lookup wrappers, credential helpers, sleep/pathconf/filesystem-info wrappers, `nfssvc` dispatch for shared common functions, compatibility stats conversion, per-vnet initialization/cleanup, ACL support probes, pNFS taskqueue dispatch, and the `nfscommon` module lifecycle.

## Global State

The file defines common NFS globals such as `newnfs_numnfsd`, `nfsstatsv1`, `nfs_numnfscbd`, `nfscl_debuglevel`, `nfsrv_lughashsize`, `nfsrv_dslock_mtx`, `nfsrv_devidhead`, `nfsrv_devidcnt`, `ncl_call_invalcaches`, `nfs_advlock_p`, `nfs_reclaim_p`, and `nfs_srvmaxio`. It defines per-vnet `nfsstatsv1_p` and references per-vnet nfsuserd socket/state.

It registers the `_vfs.nfs` sysctl node with realignment counters, debug level, user hash size, and pNFS I/O thread count. It also defines all FreeBSD `MALLOC_DEFINE()` storage classes for common NFS server/client state, file handles, lock/open/delegation state, strings, request headers, pNFS layouts/devices/sessions, and server sessions.

## Portability Wrappers

`newnfs_realign()` is a no-op on architectures that tolerate unaligned access. On strict-alignment architectures it scans an mbuf chain and, when any mbuf length or data pointer is not 4-byte aligned, copies the remaining chain into a newly allocated aligned mbuf chain and frees the original chain tail. Counters expose how often the test and realignment occur.

`nfsrv_lookupfilename()` wraps `namei()` for user-space paths. `newnfs_copycred()` copies stored NFS uid/group credentials into a FreeBSD `ucred`. `nfsmsleep()` maps a `timespec` timeout to ticks and calls `msleep()`. `newnfs_setroot()` and `newnfs_getcred()` create root-like credentials used for renew/recovery. `nfs_catnap()` implements short sleeps, using five seconds during NFS grace and one tick otherwise.

`nfsvno_getfs()` provides NFSv3 FSINFO-style server defaults, using datagram max data for UDP and `nfs_srvmaxio` otherwise. `nfsvno_pathconf()` wraps `VOP_PATHCONF()` and fakes common pathconf values instead of failing for unsupported flags. `nfsrv_atroot()` and `nfsv4root_getreferral()` are stubs in this FreeBSD port layer.

## nfssvc Dispatch And Stats Compatibility

`nfssvc_nfscommon()` switches to the caller's vnet and delegates to `nfssvc_call()`. `nfssvc_call()` handles common `nfssvc` flags:

- `NFSSVC_IDNAME` copies old or new id/name arguments and calls `nfssvc_idname()`.
- `NFSSVC_GETSTATS` copies current per-vnet `nfsstatsv1` into either old `ext_nfsstats`, older `nfsstatsov1`, or current `nfsstatsv1` user buffers, translating operation-count arrays where old layouts differ from NFSv4.2 layouts.
- `NFSSVC_ZEROCLTSTATS` and `NFSSVC_ZEROSRVSTATS` zero selected client/server statistics after a successful get-stats.
- `NFSSVC_NFSUSERDPORT` copies old or new nfsuserd port arguments and calls `nfsrv_nfsuserdport()`.
- `NFSSVC_NFSUSERDDELPORT` removes the nfsuserd port.

The stats conversion code is intentionally verbose because it maintains ABI compatibility across historical stats layouts.

## ACL And pNFS Helpers

`nfs_supportsnfsv4acls()` and `nfs_supportsposixacls()` require a locked vnode, honor the global `nfsrv_useacl` switch, call `VOP_PATHCONF()` with `_PC_ACL_NFS4` or `_PC_ACL_EXTENDED`, and return boolean support.

`nfs_pnfsio()` lazily creates a `pnfsioq` taskqueue and starts pNFS mirror I/O worker threads. If `vfs.nfs.pnfsiothreads` is negative, it defaults to `mp_ncpus * 4`; zero disables pNFS I/O dispatch. The function initializes the embedded task in the caller-provided pNFS I/O context and enqueues it, updating `inprog` according to enqueue success.

## Initialization And Module Lifecycle

`newnfs_portinit()` initializes common SMP locks once. `nfs_vnetinit()` points default-vnet stats at the global `nfsstatsv1`, allocates stats for non-default vnets, and initializes the per-vnet nfsuserd socket mutex. `nfs_cleanup()` destroys the per-vnet mutex, frees non-default stats, and cleans the name/id cache.

`nfscommon_modevent()` handles module load/unload. Load initializes mutexes, the pNFS DS lock and device list, common NFS code via `newnfs_init()`, and installs `nfssvc_nfscommon` into `nfsd_call_nfscommon`. Unload refuses while nfsd, nfsuserd, or callback daemons are active, clears the function pointer, and destroys mutexes. The module declares dependencies on `nfssvc` and `krpc`.

## Dependencies

This file depends on FreeBSD sysctl, vnet, mutex, mbuf, vnode, namei, taskqueue, VM/UMA, RPC common code, NFS id-mapping support, NFS stats structures, pNFS structures, and common NFS initialization/cleanup helpers declared elsewhere.

## Invariants And Risks

- Per-vnet stats storage differs for the default vnet and non-default vnets; cleanup must not free the global default stats.
- Old stats layouts must be kept compatible with current `nfsstatsv1`, including fake/pure NFSv4.2 operation index translations.
- `newnfs_realign()` cannot realign in place because mbuf buffers may contain adjacent RPC data; it must allocate/copy/free.
- The pNFS taskqueue is lazily initialized without an explicit teardown in this file, so repeated calls rely on the static queue pointer and module lifetime.
- Module unload must be blocked while common NFS users are active to avoid dangling function pointers or destroyed locks.
