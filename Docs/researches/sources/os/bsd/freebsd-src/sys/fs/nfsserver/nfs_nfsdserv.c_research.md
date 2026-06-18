# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_nfsdserv.c

## Role

`nfs_nfsdserv.c` is the FreeBSD NFS server operation implementation file. It contains the vnode-facing service handlers for NFSv2, NFSv3, NFSv4.0, NFSv4.1, and NFSv4.2 operations. The file is the main translation layer from decoded NFS RPC operation arguments into FreeBSD vnode/export/state-manager calls, then into XDR reply construction.

The code is organized around one handler per NFS operation, with shared helpers for symlink and mkdir creation. Most handlers follow the file header’s stated three-phase structure: parse request fields from the mbuf stream, perform vnode/state/export work through `nfsvno_*` or `nfsrv_*` helpers, and append the reply fields into the response mbuf chain.

## Major Operation Families

- Basic metadata and permission operations: `nfsrvd_access`, `nfsrvd_getattr`, `nfsrvd_setattr`, `nfsrvd_verify`.
- File-handle and lookup operations: `nfsrvd_lookup`, `nfsrvd_getfh`, `nfsrvd_openattr`.
- Data I/O operations: `nfsrvd_read`, `nfsrvd_write`, `nfsrvd_readlink`, `nfsrvd_commit`.
- Namespace mutation: `nfsrvd_create`, `nfsrvd_mknod`, `nfsrvd_remove`, `nfsrvd_rename`, `nfsrvd_link`, `nfsrvd_symlink`, `nfsrvd_mkdir`.
- Filesystem information: `nfsrvd_statfs`, `nfsrvd_fsinfo`, `nfsrvd_pathconf`.
- NFSv4 state and locking: `nfsrvd_lock`, `nfsrvd_lockt`, `nfsrvd_locku`, `nfsrvd_open`, `nfsrvd_close`, `nfsrvd_openconfirm`, `nfsrvd_opendowngrade`, `nfsrvd_releaselckown`.
- NFSv4 client/session lifecycle: `nfsrvd_setclientid`, `nfsrvd_setclientidcfrm`, `nfsrvd_exchangeid`, `nfsrvd_createsession`, `nfsrvd_sequence`, `nfsrvd_bindconnsess`, `nfsrvd_destroysession`, `nfsrvd_destroyclientid`, `nfsrvd_reclaimcomplete`.
- Delegation and pNFS layout support: `nfsrvd_delegpurge`, `nfsrvd_delegreturn`, `nfsrvd_layoutget`, `nfsrvd_layoutcommit`, `nfsrvd_layoutreturn`, `nfsrvd_layouterror`, `nfsrvd_layoutstats`, `nfsrvd_getdevinfo`.
- NFSv4.2 data-management features: `nfsrvd_allocate`, `nfsrvd_deallocate`, `nfsrvd_copy_file_range`, `nfsrvd_clone`, `nfsrvd_seek`, `nfsrvd_ioadvise`.
- NFSv4.2 extended attributes: `nfsrvd_getxattr`, `nfsrvd_setxattr`, `nfsrvd_rmxattr`, `nfsrvd_listxattr`.
- Unsupported operation stub: `nfsrvd_notsupp`.

## Key Data and Controls

The file exposes sysctls under `vfs.nfsd` that directly affect server semantics:

- `async`: can report writes as stable even when not fully synced, explicitly warned as crash-loss risky.
- `default_flexfile`: selects Flex File Layout as the default pNFS layout.
- `linux42server`: enables Linux-style NFSv4.2 compatibility behavior that can differ from RFC semantics.
- `v4openaccess`: enables Linux/OpenSolaris-style owner permission checks for NFSv4 open.
- `scope`, `owner_major`, `owner_minor`: returned in NFSv4.1 `EXCHANGE_ID`.
- `enable_v42allocate`: gates NFSv4.2 `ALLOCATE`.
- `maxcopyrange`: caps synchronous server-side copy work per RPC.

The file also relies heavily on server-wide pNFS and state globals such as `nfsrv_devidcnt`, `nfsrv_maxpnfsmirror`, `nfsrv_pnfsatime`, `nfsrv_statehashsize`, and `nfs_srvmaxio`.

## Protocol Semantics

The handlers contain many explicit protocol-version branches:

- NFSv2 and NFSv3 build post-operation attributes and weak cache consistency data using `nfsrv_postopattr()` and `nfsrv_wcc()`.
- NFSv4 uses attribute bitmaps, current stateid handling, saved/current file handles supplied by the COMPOUND dispatcher, and operation-specific error mapping.
- NFSv4.1 session operations require `SEQUENCE`, session IDs, slot IDs, and current-stateid shortcuts.
- NFSv4.2 operations implement allocation, copy, clone, seek, I/O advice, and extended attributes, with several FreeBSD/Linux compatibility branches.

Stateid handling appears throughout. The NFSv4.1 special current-stateid form, with `seqid == 1` and all-zero `other`, is repeatedly resolved from `nd->nd_curstateid` or rejected with `NFSERR_BADSTATEID`. The MDS/DS proxy stateid with all `0x55555555` and `seqid == 0xffffffff` is accepted in read, write, setattr, allocate, and deallocate paths to support pNFS proxy operations.

## Vnode and Export Interaction

Handlers are intentionally thin wrappers around lower-level helpers:

- `nfsvno_*` functions perform vnode operations, namei, attribute conversion, ACL operations, filesystem queries, and direct file operations.
- `nfsrv_*` functions perform NFSv4 state, client, delegation, session, layout, and protocol bookkeeping.
- Export checks and credential handling rely on `struct nfsexstuff`, `nfsvno_accchk()`, `nfsrv_checkuidgid()`, `nfsrv_checksetattr()`, and related helpers.

The file is careful about vnode lock ownership. Many operations explicitly unlock before acquiring another vnode, use `vrele()` versus `vput()` according to lock state, and use `vn_start_write()` / `vn_finished_write()` indirectly through the dispatcher or directly for modifying operations.

## Notable Implementation Details

- `nfsrvd_getattr()` handles referrals, named attributes, hidden/system flags, case-insensitivity, clone block size, NFSv4 ACL support, xattr support probing, and mounted-on file IDs for crossed mount points.
- `nfsrvd_setattr()` applies NFSv4 attributes in groups so the returned bitmap reflects which fields succeeded before an error.
- `nfsrvd_read()` and `nfsrvd_readlink()` can append external-page mbufs for large/TLS replies when appropriate.
- `nfsrvd_write()` honors unstable/stable write modes but can report `FILESYNC` when `vfs.nfsd.async` is enabled.
- `nfsrvd_open()` is the largest single operation: it parses owner, access/deny modes, create modes, claims, delegation wants, ACL/mode delegation ACEs, and current-stateid updates.
- `nfsrvd_copy_file_range()` and `nfsrvd_clone()` use vnode range locks to coordinate source and destination byte ranges before calling `vn_copy_file_range()`.
- `nfsrvd_listxattr()` treats the NFS cookie as an offset into a length-prefixed xattr-name buffer and validates cookie alignment against entry boundaries.

## Error Handling and Safety Notes

- The file consistently returns protocol errors through `nd->nd_repstat` and lower-level parse/transport errors through function return `error`.
- Many `nfsmout` paths release vnodes, allocated ACLs, temporary strings, or state allocations; this is central to correctness.
- Several sanity limits prevent unbounded input allocation: owner lengths, stateid counts, xattr names, layout payload sizes, max copy range, and session slot counts.
- Some compatibility behavior is intentionally non-RFC, especially Linux NFSv4.2 compatibility in copy/seek handling and the `async` write reporting option.
- The code contains diagnostic `printf("EEK...")` paths for unexpected implied-clientid inconsistencies; these indicate assumptions the surrounding session machinery should satisfy.

## Dependencies

This file depends on `nfs_nfsdsocket.c` for dispatch. The socket/COMPOUND layer selects these handlers through operation tables and supplies locked/unlocked current and saved file handles according to each operation’s flags.

It also depends heavily on other FreeBSD NFS server modules not in this group, especially vnode-portability helpers, state management, export lookup, pNFS layout/device logic, and XDR mbuf helpers declared through `<fs/nfs/nfsport.h>`.

## Research Notes

This file is a high-value map of FreeBSD NFS server behavior. For future research, the next adjacent files to inspect are the implementations of `nfsvno_*` vnode helpers, NFSv4 state management functions such as `nfsrv_lockctrl()` and `nfsrv_openctrl()`, and pNFS helpers such as `nfsrv_layoutget()` / `nfsrv_getdevinfo()`.
