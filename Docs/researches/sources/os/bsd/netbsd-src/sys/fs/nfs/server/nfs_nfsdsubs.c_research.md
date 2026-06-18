# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdsubs.c

This file provides lower-level NFS server support routines for XDR/mbuf manipulation, attribute encoding, filehandle parsing, operation-specific error filtering, name parsing, export security checks, and one-time NFS server state-table initialization.

The first half is dominated by NFSv2, NFSv3, and NFSv4 error maps. `nfsd_errmap` converts kernel errno/NFS internal errors into protocol status values, filtering NFSv3/v4 replies through operation-specific allowed-error tables. NFSv4.1 is treated differently: unsupported ops are normalized and `nfsrv_isannfserr` accepts the broader NFSv4 error range.

Serialization helpers include `nfsrv_adj` for trimming mbuf chains with optional zero-fill, `nfsrv_wcc` and `nfsrv_postopattr` for weak-cache-consistency/post-op attributes, `nfsrv_fillattr` for NFSv2/v3 fattr encoding, and `nfsrv_mtofh` for extracting fixed or counted filehandles, including public-filehandle lookup handling.

NFSv4-specific helpers include `nfsrv_checkuidgid` and `nfsrv_fixattr` for owner/group/time/ACL setattr policy, `nfsrv_errmoved` and `nfsrv_putreferralattr` for referral attributes, `nfsrv_parsename` for component-name extraction and validation, and `nfsd_getminorvers` for parsing the start of a compound and setting the NFSv4.1 flag. UTF-8, nobody, and nogroup checks are sysctl-controlled.

`nfsd_init` allocates and initializes the client, lock-file, and session hash tables used by `nfs_nfsdstate.c`. `nfsd_checkrootexp` checks that a request's security flavor is allowed by the NFSv4 pseudo-root export.

Integration points: used by most NFS server operation handlers and by the NFSv4 state code. It is a protocol boundary file: it translates between mbuf/XDR wire data, NetBSD vnode attributes, kernel credentials, export flags, and NFS status codes.

Risks: the error-map arrays are indexed by protocol operation numbers, so ordering drift is a high-impact maintenance hazard. `nfsrv_fixattr` temporarily mutates `nd_cred->cr_uid` to perform allowed group changes and must restore it. Public-filehandle name parsing includes percent-decoding and slash rules, so small changes can alter externally visible lookup behavior. Disabling UTF-8/nobody/nogroup sysctls relaxes RFC/policy checks.
