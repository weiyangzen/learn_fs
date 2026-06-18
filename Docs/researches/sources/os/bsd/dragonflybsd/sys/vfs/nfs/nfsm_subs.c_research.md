# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfsm_subs.c

## Purpose

`nfsm_subs.c` implements the mbuf/XDR marshalling and unmarshalling helper routines used by both NFS client and server code. It builds RPC headers, appends file handles/strings/uio/bio payloads, parses replies and requests, handles weak cache consistency fields, and formats server replies.

## Main Contents

- Request construction:
  - `nfsm_reqhead()` starts an NFS request mbuf chain.
  - `nfsm_rpchead()` builds the SunRPC call header, assigns XIDs, maps generic NFS proc ids to v2/v3, and encodes UNIX or Kerberos auth plus verifier.
  - `nfsm_build()` appends fixed-size fields to the current mbuf.
  - `nfsm_fhtom()`, `nfsm_srvfhtom()`, and `nfsm_srvpostop_fh()` encode client/server file handles.
  - `nfsm_strtom()` and `nfsm_strtmbuf()` encode counted, padded NFS strings.
  - `nfsm_uiotom()`/`nfsm_biotom()` and lower-level `nfsm_uiotombuf()`/`nfsm_biotombuf()` copy uio or bio payloads into mbuf chains.
- Reply/request parsing:
  - `nfsm_dissect()` extracts fixed-size fields, using `nfsm_disct()` when data spans mbufs.
  - `nfsm_getfh()` parses v2/v3 file handles.
  - `nfsm_mtofh()` parses optional v3 post-op file handles, creates/gets nfsnodes, and loads attributes.
  - `nfsm_strsiz()`, `nfsm_srvstrsiz()`, and `nfsm_srvnamesiz()` validate counted string lengths.
  - `nfsm_mtouio()`/`nfsm_mtobio()` and lower-level `nfsm_mbuftouio()`/`nfsm_mbuftobio()` copy mbuf payloads into uio or bio buffers.
  - `nfsm_adv()` and `nfs_adv()` skip padded data in mbuf chains.
  - `nfsm_srvmtofh()` parses server-side file handles from client requests.
  - `nfsm_srvsattr()` parses NFSv3 setattr structures into `struct vattr`.
- Request execution:
  - `nfsm_request()` initializes `struct nfsm_info` and runs `nfs_request()` synchronously to completion.
  - `nfsm_request_bio()` starts the state machine for async BIO-backed operations and completes the BIO itself on early failure.
- Attribute and WCC handling:
  - `nfsm_loadattr()` updates the attribute cache from reply data.
  - `nfsm_postop_attr()` handles optional NFSv3 post-operation attributes.
  - `nfsm_wcc_data()` decodes v3 weak-cache-consistency data and marks `NRMODIFIED` when server-side before-time mismatches local expectations.
  - `nfsm_v3attrbuild()` builds NFSv3 setattr fields from `struct vattr`.
- Server reply formatting:
  - `nfsm_reply()` and `nfsm_writereply()` build RPC reply headers.
  - `nfsm_srvwcc_data()`, `nfsm_srvpostop_attr()`, and `nfsm_srvfattr()` encode v3 WCC/postop attributes and v2/v3 file attributes.

## Notable Details

- XID generation starts from `krandom()` and uses `atomic_fetchadd_int()`, avoiding zero.
- Helper routines commonly free `info->mrep` or `info->mreq` on parse/build failures to simplify caller cleanup.
- `nfsm_disct()` may splice a new mbuf into the reply chain to create contiguous data for fields crossing mbuf boundaries.
- Many routines assume NFS's 4-byte XDR padding and use `nfsm_rndup()`.
- `nfsm_uiotombuf()` asserts a single iovec under diagnostic builds.
- `nfsm_srvfattr()` clamps link counts above 65535, reflecting NFS field-size behavior.
- Server-side name parsing distinguishes malformed RPC (`EBADRPC`) from valid NFS errors such as `NFSERR_NAMETOL`.

## Integration

This is the central utility layer for `nfs_vnops.c`, `nfs_vfsops.c`, server procedures in `nfs_serv.c`, socket/request state in `nfs_socket.c`, and cache/attribute handling in `nfs_node.c` and related NFS modules.
