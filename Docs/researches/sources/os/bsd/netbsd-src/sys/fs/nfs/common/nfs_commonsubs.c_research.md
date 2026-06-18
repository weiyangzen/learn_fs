# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_commonsubs.c

This is the main common NFS protocol helper body. It handles XDR/mbuf construction and dissection, NFSv4 attribute parsing/emission, owner/group string mapping, NFSv4 common locks, NFSv4.1 session sequencing, socket send locks, UTF-8 checks, and common reply setup.

Key contents:
- Defines shared XDR constants (`newnfs_true`, `newnfs_false`, `newnfs_xdrneg1`), type conversion tables, `nfsboottime`, `nfscl_ticks`, `nfsrv_useacl`, `nfsrv_lease`, `nfs_bigreply`, and the NFSv4 operation flag table `nfsv4_opflag`.
- Implements mbuf/uio helpers: `nfsm_mbufuio()`, `nfsm_dissct()`, `nfsm_advance()`, `nfsm_strtom()`, `nfsm_fhtom()`, `nfsrv_mtostr()`, `newnfs_trimleading()`, and `newnfs_trimtrailing()`.
- Implements address comparison helpers for IPv4 and IPv6: `nfsaddr_match()` and `nfsaddr2_match()`.
- Implements NFSv4 ACL and attribute parsing through `nfsrv_dissectacl()`, `nfsrv_skipace()`, `nfsrv_getattrbits()`, and the large `nfsv4_loadattr()` switch over NFSv4 attribute bits.
- Implements NFSv4 attribute emission through `nfsv4_fillattr()` and `nfsrv_putattrbit()`, including statfs-derived values, ACL support, quota-aware fields under `QUOTA`, owner/group names, file handles, times, fileids, and pNFS-related attributes.
- Implements a lightweight common lock/reference primitive for NFSv4 state structures: `nfsv4_lock()`, `nfsv4_unlock()`, `nfsv4_relref()`, `nfsv4_getref()`, `nfsv4_getref_nonblock()`, and `nfsv4_testlock()`.
- Implements uid/gid string conversion and caching: `nfsv4_uidtostr()`, `nfsv4_strtouid()`, `nfsv4_gidtostr()`, `nfsv4_strtogid()`, `nfsrv_getgrpscred()`, `nfssvc_idname()`, `nfsrv_removeuser()`, and `nfsrv_cleanusergroup()`.
- Handles `nfsuserd` connection/upcalls with `nfsrv_nfsuserdport()`, `nfsrv_nfsuserddelport()`, and `nfsrv_getuser()`.
- Implements UTF-8 validation in `nfsrv_checkutf8()`.
- Parses NFSv4 `fs_locations` strings in `nfsrv_getrefstr()` and grows buffers via `nfsrv_refstrbigenough()`.
- Initializes reply mbufs in `nfsrvd_rephead()`, choosing clusters for known large replies.
- Provides socket serialization with `newnfs_sndlock()` and `newnfs_sndunlock()`.
- Parses NFSv4.1 callback network addresses in `nfsv4_getipaddr()`.
- Implements NFSv4.1 sequence/session slot helpers: `nfsv4_seqsession()`, `nfsv4_seqsess_cacherep()`, `nfsv4_setsequence()`, `nfsv4_sequencelookup()`, and `nfsv4_freeslot()`.

Important dependencies:
- Uses macros from `nfsm_subs.h` and porting types from `nfsport.h`/`nfskpiport.h`.
- Uses ACL helpers declared in `nfs_var.h`: `nfsrv_dissectace()`, `nfsrv_buildacl()`, and `nfsrv_compareacl()`.
- `nfssvc_idname()` is reached through `nfs_commonport.c` and `nfssvc(2)`.

Risks and notes:
- `nfsv4_loadattr()` and `nfsv4_fillattr()` are protocol-critical, long switch statements; new NFSv4 attributes require synchronized parse/fill behavior and size accounting.
- The id/name cache uses four hash tables with explicit lock ordering. The comments document the lock order; violating it risks deadlock.
- Several compatibility decisions are embedded, such as accepting numeric owner strings only for AUTH_SYS/client cases or when enabled by `nfsd_enable_stringtouid`.
