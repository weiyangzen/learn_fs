# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_subr.c

## Purpose
Contains the shared NFS client support substrate: RPC client-handle caching, NFSv2/v3 and ACL RPC call loops, rnode/filehandle caches, access and readdir caches, memory reclaim, failover, custom NFS rwlocks, status conversion, zone setup, mount label policy, and assorted vnode helper routines.

## Key Elements
The RPC layer centers on `clget_impl`, `clfree_impl`, `nfs_clget`, `acl_clget`, `rfscall`, and `aclcall`. It caches kernel RPC `CLIENT` handles per zone by program/version/transport/protocol family, attaches security handles with `sec_clnt_geth`, reclaims idle handles under memory pressure, and records client stats. `rfscall` and `aclcall` implement hard/soft/semisoft mount retry behavior, interrupt handling, timeout backoff, server down/up messages, adaptive read/write transfer-size feedback, TSOL credential cloning with `NET_MAC_AWARE`, forced-unmount/zone-shutdown bailouts, and failover retries. `rfs2call`, `rfs3call`, `acl2call`, and `acl3call` add protocol-level status handling, credential network adjustment retries, NFSv3 jukebox delay loops, and NFSv2 procedure-unavailable mapping.

The rnode layer uses a Jenkins one-at-a-time hash over NFS filehandles, per-bucket rwlocks, a freelist protected by `rpfreelist_lock`, and an `rnode_cache`. `makenfsnode`, `makenfs3node`, and `makenfs3node_va` find or create vnodes/rnodes, cache attributes, set vnode type/device data, and store failover pathnames when needed. `rp_addfree`, `rp_addhash`, `rp_rmhash`, `rfind`, `destroy_rtable`, `rflush`, and `destroy_rnode` manage vnode references, hash membership, VFS holds, dirty page flushing, and safe destruction.

Cache helpers include `nfs_access_check`, `nfs_access_cache`, `nfs_access_purge_rp`, `rddir_cache_alloc`, `rddir_cache_hold`, `rddir_cache_rele`, and debug buffer accounting. Memory reclaim frees cached credentials, symlink contents, ACLs, pathconf data, access entries, readdir caches, and finally unused rnodes if lighter reclamation is insufficient.

Failover support includes filehandle copy callbacks, `failover_safe`, `failover_newserver`, `failover_thread`, `failover_wait`, `failover_remap`, and `failover_lookup`. It selects a responsive replica, updates root and non-root rnodes to new filehandles, purges DNLC data, validates remapped object type/size, preserves cached attributes where possible, and updates operation argument filehandles via `failinfo_t`.

Other utilities convert `vattr` to NFSv2/NFSv3 setattr structures, choose inherited directory group/mode behavior, mark swap-like files, generate `.nfs...` temporary names, initialize/finalize global tables and per-zone client state, convert errno/NFS statuses for v2 and v3, free `servinfo_t` chains, implement recursive writer-aware `nfs_rwlock_t`, compare cached readdir cookies, select global-zone client behavior for the upgrade workaround, enforce Trusted Extensions mount label policy, test for a controlling terminal, check extended-attribute directory contents, and return NFS uptime.

## Dependencies
Depends on illumos vnode/VFS/page/DNLC/session/zone/label/TSOL primitives, RPC client APIs, NFS v2/v3/v4 protocol headers, NFS ACL support, rnode/mount structures, kernel memory caches, kstats, credentials/security handles, server replica metadata, synchronization primitives, and path/dirent helpers.

## Behavior/Risks
This file is highly concurrency-sensitive. Rnode hash locks, vnode locks, freelist locks, mount rnode-list locks, and per-rnode state locks have documented ordering constraints; violating them risks deadlock or use-after-free. The failover code depends on stored pathnames matching replica namespace layout and validates only type/size as a heuristic, so remapping behavior is deliberately conservative. RPC retry logic must preserve hard-mount semantics without blocking shutdown/unmount paths forever. The client-handle cache spans zone lifecycle ordering concerns, which is why `clcleanup_zone` exists separately from ZSD destruction. Status conversion has debug and non-debug differences; callers must not assume every protocol status maps uniquely to errno.
