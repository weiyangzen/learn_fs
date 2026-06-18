# File Research: sources/os/bsd/freebsd-src/sys/fs/nfs/nfs_commonsubs.c

This file is the common NFS client/server protocol support layer. It builds and parses RPC/XDR mbuf chains, translates NFSv2/v3/v4 attributes and file handles, manages NFSv4.1 session sequencing, handles NFSv4 owner/owner-group name mapping, and provides small shared synchronization helpers used by both client and server code.

Key behavior:
- Defines global NFS constants and mapping tables: XDR booleans, vnode/NFS type maps, NFSv4 operation metadata, large-request/reply hints, NFSv4 minor-version operation maps, and initial root/bin/wheel/operator id-name mappings.
- `nfscl_reqstart()` initializes an `nfsrv_descript` and builds the leading NFS request for v2/v3/v4, including NFSv4 compound tags, operation counts, `Sequence`, `PutFH`, and optional weak-cache-consistency `Getattr` operations.
- `nfsm_strtom()`, `nfsm_fhtom()`, `nfsm_mbufuio()`, `nfsm_dissct()`, `nfsm_advance()`, `nfsrv_mtostr()`, `nfsm_set()`, and `nfsm_add_ext_pgs()` are the low-level mbuf/XDR construction and dissection helpers, including support for external-page mbufs.
- `nfsm_stateidtom()` serializes special and normal NFSv4 stateids.
- `nfscl_fillsattr()` serializes settable attributes for NFSv2, NFSv3, and NFSv4, including size/rdev special cases, timestamp policy, owner/group, mode, flags, birthtime, and NFSv4 `mode_umask` handling.
- `nfsv4_loadattr()` parses NFSv4 attributes into `nfsvattr`, statfs/fsinfo/pathconf structures, ACLs, file handles, lease values, clone block size, true ACL form, named-attribute state, and read-directory attribute errors. In compare mode it validates wire attributes against local vnode/filesystem state.
- `nfsv4_fillattr()` emits NFSv4 attributes from vnode attributes, export/filesystem state, ACL support, pathconf-derived capabilities, pNFS layout information, quotas, xattr support, and filesystem statistics.
- `nfsrv_getattrbits()`, `nfsrv_putattrbit()`, `nfsrv_getopbits()`, and `nfsrv_putopbit()` parse and serialize NFSv4 bitmap attribute/operation sets.
- `nfsrv_dissectacl()` parses NFSv4 or POSIX draft ACL wire data, optionally discarding unsupported or oversized ACLs while still advancing the XDR stream.
- `nfsv4_uidtostr()`, `nfsv4_gidtostr()`, `nfsv4_strtouid()`, and `nfsv4_strtogid()` translate between numeric ids and NFSv4 owner strings using cached mappings, `nfsuserd`, domain suffix logic, and numeric fallback rules.
- `nfsrv_nfsuserdport()`, `nfsrv_nfsuserddelport()`, `nfsrv_getuser()`, `nfssvc_idname()`, `nfsrv_removeuser()`, and `nfsrv_cleanusergroup()` manage per-vnet id/name hash tables, nfsuserd upcalls, default nobody/nogroup identities, cache expiration, approximate LRU trimming, and teardown.
- `nfsv4_lock()`, `nfsv4_unlock()`, `nfsv4_getref()`, `nfsv4_getref_nonblock()`, `nfsv4_relref()`, and `nfsv4_testlock()` implement a small NFSv4 shared-reference/exclusive-sleep-lock primitive.
- `nfsrv_checkutf8()` validates NFSv4 UTF-8 strings, including continuation-byte and surrogate range checks.
- `nfsrv_getrefstr()` parses `fs_locations` referral attributes into internal root/server-list strings.
- `nfsrvd_rephead()` initializes server reply mbufs, using clusters or external pages for large replies.
- `newnfs_sndlock()` / `newnfs_sndunlock()` serialize socket connect/disconnect style operations.
- `nfsv4_getipaddr()` parses NFSv4 network address strings into IPv4/IPv6 socket addresses and protocol selection.
- `nfsv4_seqsession()`, `nfsv4_seqsess_cacherep()`, `nfsv4_setsequence()`, `nfsv4_sequencelookup()`, and `nfsv4_freeslot()` implement NFSv4.1 session slot sequencing, retry detection, cached replies, bad-slot handling, and forced-dismount escape paths.
- `nfsv4_findmirror()` searches pNFS device state for a matching data-server mount.
- `nfsrpc_destroysession()` sends an NFSv4.1 `DestroySession` compound.
- `nfs_trueform()`, `vtonfsv4_type()`, and `nfsv4tov_type()` convert ACL model and vnode/file types, including named attribute directory/file encodings.

Important interactions:
- Uses `nfsm_subs.h` macros and `struct nfsrv_descript` cursor fields for all mbuf building/parsing.
- Declares and implements many prototypes exposed through `nfs_var.h`.
- Depends on vnode/VFS operations for ACLs, pathconf, statfs, quota checks, and mounted-on-fileid behavior.
- Interacts with `nfsuserd(8)` through a loopback RPC socket for NFSv4 id-name translation.
- Uses per-vnet globals for name caches and defaults, so jail/vnet teardown must call `nfsrv_cleanusergroup()`.
- Coordinates with NFSv4.1 client session state in `struct nfsclsession`, including MDS/DS sessions and pNFS behavior.
- Uses the `nfsv4_opflag` table to drive server/client compound construction, current file-handle needs, sequencing, and reply cache expectations.

Edge cases:
- Many parsers cap untrusted counts and lengths, such as ACL entries, owner/group strings, attr bitmap words, referral strings, server lists, and network address strings.
- Attribute compare mode deliberately maps unsupported ACLs, hidden/system flags, clone block size, and pNFS layout support to protocol errors such as `NFSERR_ATTRNOTSUPP` or `NFSERR_NOTSAME`.
- Numeric owner/group strings are accepted only for AUTH_SYS/client-side or explicitly enabled server-side string-to-id cases, not Kerberos.
- Some known nonconforming server values are normalized, for example extreme or zero `maxname`.
- Session sequencing treats duplicate seqids as retries, can return cached replies, and returns `NFSERR_SEQMISORDERED` when all usable slots are bad.
- Forced unmount paths avoid indefinite waits in lock/reference and session-slot acquisition loops.
- The id-name cache uses careful lock ordering across name and id hash tables to avoid lock-order reversals.
